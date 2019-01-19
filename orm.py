import pymysql

"""
Notes:
命名?
异常完善?
重构?
and or?
sort?
"""

"""
约定:
    一个模型必须有id,类型为PrimaryKeyField作为它的主键
    不能自己在模型里面自己定义任何方法,或不属于Fields类型的字段
"""

def Mysql(host, user, password, database):
    return pymysql.connect(host, user, password, database)

# 将值转安全转意,防止注入
def safe(value):
    if isinstance(value, str):
        return pymysql.escape_string(value)
    else:
        return value

# ===Fields===
class TextField:
    def __init__(self, nullable=True, unique=False):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique

    # 每个字段都实现这个方法:获取这个字段的单独建表元素比如username VARCHAR(255) NOT NULL UNIQUE
    def _make_element(self):
        sentence = '{} TEXT'.format(self.fieldname)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    # 每个字段都实现这个方法:检查值是否符合要求
    def _check(self, value):
        # 类型不匹配或者nullable=False且值为空都不能通过验证
        if isinstance(value, str) or (value is None and self.nullable):
            return True
        return False
    
    # 每个字段都实现这个方法:获取这个字段值的表达式比如INT和FLOAT分别是1,1.0,而TEXT,VARCHAR是'1'
    def _value(self, value):
        return "'{}'".format(value)
    
    def __eq__(self, value):
        return '{}={}'.format(self.fieldname, self._value(value))
    
    def __ne__(self, value):
        return '{}!={}'.format(self.fieldname, self._value(value))

class VarcharField:
    def __init__(self, max_length=256, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.max_length = max_length
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '{} VARCHAR({})'.format(self.fieldname, self.max_length)
        if self.default is not None:
            sentence += " DEFAULT '{}'".format(self.default)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    def _check(self, value):
        if isinstance(value, str) or (value is None and self.nullable):
            return True
        return False
    
    def _value(self, value):
        return "'{}'".format(value)
    
    def __eq__(self, value):
        return '{}={}'.format(self.fieldname, self._value(value))
    
    def __ne__(self, value):
        return '{}!={}'.format(self.fieldname, self._value(value))
        
class IntField:
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '{} INT'.format(self.fieldname)
        if self.default is not None:
            sentence += " DEFAULT {}".format(self.default)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence
    
    def _check(self, value):
        if isinstance(value, int) or (value is None and self.nullable):
            return True
        return False
    
    def _value(self, value):
        return "{}".format(value)

    def __eq__(self, value):
        return '{}={}'.format(self.fieldname, self._value(value))
    
    def __ne__(self, value):
        return '{}!={}'.format(self.fieldname, self._value(value))
    
    def __gt__(self, value):
        return '{}>{}'.format(self.fieldname, self._value(value))
    
    def __lt__(self, value):
        return '{}<{}'.format(self.fieldname, self._value(value))
    
    def __ge__(self, value):
        return '{}>={}'.format(self.fieldname, self._value(value))

    def __le__(self, value):
        return '{}<={}'.format(self.fieldname, self._value(value))

class FloatField:
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '{} FLOAT'.format(self.fieldname)
        if self.default is not None:
            sentence += " DEFAULT {}".format(self.default)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence
    
    def _check(self, value):
        if isinstance(value, float) or (value is None and self.nullable):
            return True
        return False
    
    def _value(self, value):
        return "{}".format(value)
    
    def __eq__(self, value):
        return '{}={}'.format(self.fieldname, self._value(value))
    
    def __ne__(self, value):
        return '{}!={}'.format(self.fieldname, self._value(value))
    
    def __gt__(self, value):
        return '{}>{}'.format(self.fieldname, self._value(value))
    
    def __lt__(self, value):
        return '{}<{}'.format(self.fieldname, self._value(value))
    
    def __ge__(self, value):
        return '{}>={}'.format(self.fieldname, self._value(value))

    def __le__(self, value):
        return '{}<={}'.format(self.fieldname, self._value(value))

class PrimaryKeyField():
    def __init__(self):
        self.fieldname = 'id'
    
    def _check(self, value):
        if isinstance(value, int) or value is None:
            return True
        return False
    
    def _value(self, value):
        return '{}'.format(value)
    
    def _make_element(self):
        return '{} INT NOT NULL AUTO_INCREMENT PRIMARY KEY'.format(self.fieldname)
    
    def __eq__(self, value):
        return '{}={}'.format(self.fieldname, self._value(value))
    
    def __ne__(self, value):
        return '{}!={}'.format(self.fieldname, self._value(value))
    
    def __gt__(self, value):
        return '{}>{}'.format(self.fieldname, self._value(value))
    
    def __lt__(self, value):
        return '{}<{}'.format(self.fieldname, self._value(value))
    
    def __ge__(self, value):
        return '{}>={}'.format(self.fieldname, self._value(value))

    def __le__(self, value):
        return '{}<={}'.format(self.fieldname, self._value(value))
        

field_types = (TextField, VarcharField, IntField, FloatField, PrimaryKeyField)
# ============

class Base:
    class Meta:
        db = None
        table = None

    # 在每个操作里面都检查是否init,仅仅执行一次init
    _init_sign = False
    _fields = {}

    # 接收本对象的各个字段值,没有赋值的默认为None
    def __init__(self, **kwargs):
        self.__class__._init()
        # 靠id来判断该对象是否已经被插入进数据库了,如果为None则还未被插入
        fields = self.__class__._get_fields()
        fieldnames = fields.keys()
        for key in kwargs.keys():
            if key not in fieldnames:
                raise Exception('未知的参数{}'.format(key))
        for key,value in fields.items():
            self.__setattr__(key,kwargs.get(key, None))

    # 将字段名写入_field,将字段名写入对应字段对象,并标记已初始化
    @classmethod
    def _init(cla):
        if not cla._init_sign:
            for key,value in cla.__dict__.items():
                if isinstance(value, field_types):
                    value.fieldname = key
                    cla._fields[key] = value
            cla._init_sign = True

    # 获取_fields
    @classmethod
    def _get_fields(cla):
        return cla._fields
    
    # 获取当前对象的数据
    def _get_current_data(self):
        fields = self.__class__._get_fields()
        res = {}
        for fieldname in fields.keys():
            value = self.__getattribute__(fieldname)
            # 防止没有赋值该属性导致被类变量覆盖
            if not isinstance(value,field_types):
                res[fieldname] = self.__getattribute__(fieldname)
            else:
                res[fieldname] = None
        return res

    @classmethod
    def create_table(cla):
        cla._init()
        db = cla.Meta.db
        table = cla.Meta.table
        cursor = db.cursor()
        fields = cla._get_fields()

        field_elements = []
        for key,value in fields.items():
            field_elements.append(value._make_element())
        
        sentence = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(table, ','.join(field_elements))
        cursor.execute(sentence)
    
    @classmethod
    def drop_table(cla):
        cla._init()
        table = cla.Meta.table
        cursor = cla.Meta.db.cursor()

        sentence = 'DROP TABLE IF EXISTS {}'.format(table)
        cursor.execute(sentence)
    
    def insert(self):
        self.__class__._init()
        db = self.__class__.Meta.db
        table = self.__class__.Meta.table
        cursor = db.cursor()
        data = self._get_current_data()
        fields = self.__class__._get_fields()

        fieldnames = []
        values = []
        # 类型检查
        for key,value in fields.items():
            if value._check(data.get(key)):
                if key == 'id':
                    continue
                fieldnames.append(key)
                values.append(value._value((safe((data.get(key))))))
            else:
                raise TypeError('类型不匹配')
        fieldnames_str = ','.join(fieldnames)
        values_str = ','.join(values)
        sentence = 'INSERT INTO {} ({}) VALUES({})'.format(table, fieldnames_str, values_str)
        cursor.execute(sentence)
        db.commit()
    
    @classmethod
    def search(cla, *querys):
        cla._init()
        table = cla.Meta.table
        cursor = cla.Meta.db.cursor()
        fieldnames = cla._get_fields().keys()
        
        conditions = []

        for query in querys:
            conditions.append(safe(query))

        temp1 = ','.join(fieldnames)
        temp2 = ' and '.join(querys)
        if querys:
            sentence = 'SELECT {} FROM {} WHERE {}'.format(temp1, table, temp2)
        else:
            sentence = 'SELECT {} FROM {}'.format(temp1, table, temp2)
        if cursor.execute(sentence) == 0:
            return []
        all_data = cursor.fetchall()
        res = []
        for one in all_data:
            one = list(one)
            obj = cla()
            index = 0
            while index <= len(fieldnames)-1:
                obj.__setattr__(list(fieldnames)[index], one[index])
                index += 1
            res.append(obj)
        return res
    
    def update(self):
        self.__class__._init()
        db = self.__class__.Meta.db
        table = self.__class__.Meta.table
        cursor = db.cursor()
        if self.id == None:
            raise Exception('该对象不可更新')
        fields = self.__class__._get_fields()
        current_data = self._get_current_data()
        sets = []
        for field in fields.values():
            value = current_data.get(field.fieldname)
            if not field._check(value):
                raise TypeError('类型错误')
            sets.append('{}={}'.format(field.fieldname,field._value(safe(value))))
        temp = ','.join(sets)
        sentence = 'UPDATE {} SET {} WHERE id={}'.format(table, temp, str(self.id))
        cursor.execute(sentence)
        db.commit()
    
    def delete(self):
        self.__class__._init()
        db = self.__class__.Meta.db
        table = self.__class__.Meta.table
        cursor = db.cursor()

        if self.id == None:
            raise Exception('此对象不可删除')
        
        sentence = 'DELETE FROM {} WHERE id={}'.format(table, self.id)
        cursor.execute(sentence)
        db.commit()
