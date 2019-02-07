##### [中文-Chinese](https://github.com/lwaix/Pmorm/blob/master/README-zh.md "中文-Chinese")

# pmorm.py - a simple mysql orm for python3

## Installing

```
python3 .\setup.py install --user
```

## Usage

### Before using

#### Create a database for the program

```
mysql>CREATE DATABASE testdb;
```

### Quick start

#### Create a mysql database connection

```python
from pmorm import Mysql

mydb = Mysql('localhost', 'root', 'your-passwd', 'testdb')
```

#### Create a model and create the table

```python
from pmorm import Base, PrimaryKeyField, VarcharField

# Model class
class User(Base):
    # Built-in class Meta for configuring database and table
    class Meta:
        db = mydb
        table = 'user'

    # Define fields in a model
    id = PrimaryKeyField()  # id field must be defined like this
    username = VarcharField(max_length=32, nullable=False, unique=True, default=None)
    password = VarcharField(max_length=64, nullable=False, unique=False, default=None)

# Create table if it hasn't been created
User.create_table()
```

#### Inserting

```python
# A easy way
user1 = User(username='user1', password='passwd1')
user1.insert()

# Another way
user2 = User()
user2.username = 'user2'
user2.password = 'passwd2'
user2.insert()

# Modify it before inserting
user3 = User(username='userx')
user3.username = 'user3'
user3.password = 'passwd3'
user3.insert()

# Cheak if objects has been inserted
print(user1.inserted()) # True
```

#### Search rows

```python
# Get all and print them one by one
users = User.search().all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

# Search by one condition
users = User.search(User.username != 'unkonw').all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

# Search by conditions of the combination(using & and | operators)
user1 = User.search(
    (User.username=='user1') & (User.password=='passwd1')
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))

# Sort by using the "orders" option
users = User.search(
    (User.username!='user1') | (User.password!='passwd1'),
    orders=[User.id]
).all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))
```

##### Attention: search() return a "Result" object, you can get specific data by its methods all() and first()

#### Editing

```python
# Get one user first
user1 = User.search(
    ((User.username=='user1') | (User.password=='passwd1') & (User.id==1)) # Complex queries
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))
# Edit it and update
user1.username = 'edit'
user1.update()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))
```

#### Deleting

```python
user1.delete()
```

### About Mysql() function

#### The code of Mysql() function

```python
def Mysql(*args, **kwargs):
    return pymysql.connect(*args, **kwargs)
```

#### The Mysql() function is actually the encapsulation of the pymysql.connect() function, which has more parameters, see pymysql documentation

### Currently supported MySQL fields

Pmorm|Mysql
--|:--:
PrimaryKeyField|NO
IntField|INT
FloatField|FLOAT
VarcharField|VARCHAR
TextField|TEXT

#### PrimaryKeyField must be defined in each model, so a basic model looks like...

```python
mydb = Mysql('localhost', 'root', 'your-passwd', 'your-database')
class ModelName(Base):
    class Meta:
        db = mydb
        table = 'mytable'
    id = PrimaryKeyField()
    # Other fields...
```