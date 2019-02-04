import peewee
import peewee_async
from datetime import datetime, timedelta
import logging
import csv
import io

from .settings import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST


db = peewee_async.PooledPostgresqlDatabase(
    DB_NAME,
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    max_connections=20,
    autorollback=True)

manager = peewee_async.Manager(db)
manager.database.allow_sync = logging.WARNING


class Base(peewee.Model):
    class Meta:
        database = db


class User(Base):
    id = peewee.PrimaryKeyField()
    name = peewee.CharField()
    username = peewee.CharField(null=True)
    registration = peewee.DateTimeField(default=datetime.now)
    admin = peewee.BooleanField(default=False)

    @classmethod
    async def save_user(cls, user):
        try:
            _user = await manager.get(cls, id=user.id)
        except cls.DoesNotExist:
            _user = await manager.create(
                    cls,
                    id=user.id,
                    name=user.first_name,
                    username=user.username
                )
        return _user


class Group(Base):
    id = peewee.BigIntegerField(primary_key=True)
    title = peewee.CharField()
    # TODO delete filed link
    link = peewee.CharField(null=True)
    registration = peewee.DateTimeField(default=datetime.now)
    deleted = peewee.BooleanField(default=False)

    @classmethod
    async def save_group(cls, group, readded=False):
        try:
            _group = await manager.get(cls, id=group.id)
        except cls.DoesNotExist:
            _group = await manager.create(
                    cls,
                    id=group.id,
                    title=group.title,
                    username=group.username
                )
        else:
            if readded:
                _group.deleted = False
                await manager.update(_group)
        return _group

    @classmethod
    async def delete_group(cls, group_id):
        async with manager.transaction():
            try:
                group = await manager.get(
                    cls,
                    id=group_id
                    )
            except cls.DoesNotExist:
                return

            group.deleted = True
            await manager.update(group)

    @classmethod
    async def download_data(cls, cid):
        group_data = await manager.execute(
            cls.select(
                User.id, User.name, User.username,
                UserToGroup.registration, UserToGroup.deleted
                ).join(UserToGroup).join(User).where(
                UserToGroup.group == cid
            ).dicts()
        )

        with io.StringIO() as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'username',
                'registration', 'deleted'])
            writer.writeheader()
            writer.writerows(group_data)
            f.seek(0)
            return f.getvalue().encode()


class UserToGroup(Base):
    user = peewee.ForeignKeyField(User, related_name='to_user', on_delete='CASCADE')
    group = peewee.ForeignKeyField(Group, related_name='to_group', on_delete='CASCADE')
    registration = peewee.DateTimeField(default=datetime.now)
    deleted = peewee.BooleanField(default=False)

    @classmethod
    async def save_user_to_group(cls, user, group):
        async with manager.transaction():
            await User.save_user(user)
            await Group.save_group(group)
            try:
                _group = await manager.get(cls, user=user.id, group=group.id)
            except cls.DoesNotExist:
                await manager.create(
                    cls,
                    user=user.id,
                    group=group.id)
            else:
                _group.deleted = False
                _group.registration = datetime.now()
                await manager.update(_group)

    @classmethod
    async def save_new_user(cls, user, group):
        async with manager.transaction():
            await User.save_user(user)
            await Group.save_group(group)
            try:
                await manager.get(cls, user=user.id, group=group.id)
            except cls.DoesNotExist:
                await manager.create(
                    cls,
                    user=user.id,
                    group=group.id)

    @classmethod
    async def delete_user_from_group(cls, user_id, group_id):
        async with manager.transaction():
            try:
                user_group = await manager.get(
                    cls,
                    user=user_id,
                    group=group_id
                    )
            except cls.DoesNotExist:
                return

            user_group.deleted = True
            await manager.update(user_group)

    @classmethod
    async def can_send_sticker(cls, user, group):
        try:
            group_user = await manager.get(
                             cls,
                             group=group.id,
                             user=user.id
                         )
        except cls.DoesNotExist:
            await cls.save_user_to_group(user, group)
            return True
        else:
            return group_user.registration < datetime.now() + timedelta(days=7)


class Link(Base):
    group = peewee.ForeignKeyField(Group, related_name='link_group', on_delete='CASCADE')
    url = peewee.CharField(primary_key=True)


if __name__ == "__main__":
    with manager.allow_sync():
        User.create_table(True)
        Group.create_table(True)
        UserToGroup.create_table(True)
        Link.create_table(True)
