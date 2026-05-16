import sqlite3
from config import DATABASE

skills = [ (_,) for _ in (['Python', 'SQL', 'API', 'Telegram'])]
statuses = [ (_,) for _ in (['На этапе проектирования', 'В процессе разработки', 'Разработан. Готов к использованию.', 'Обновлен', 'Завершен. Не поддерживается'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                        project_id INTEGER PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        project_name TEXT NOT NULL,
                        description TEXT,
                        url TEXT,
                        status_id INTEGER,  
                        FOREIGN KEY(status_id) REFERENCES status(status_id)
                    )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                        skill_id INTEGER PRIMARY KEY,
                        skill_name TEXT UNIQUE
                    )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                        project_id INTEGER,
                        skill_id INTEGER,
                        FOREIGN KEY(project_id) REFERENCES projects(project_id),
                        FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                    )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS status (
                        status_id INTEGER PRIMARY KEY,
                        status_name TEXT UNIQUE
                    )''')
        conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skills (skill_name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)


    def insert_project(self, data):
        sql = '''INSERT INTO projects (user_id, project_name, description, url, status_id ) values(?,?,?,?,?)'''
        self.__executemany(sql, data)


    def insert_skill(self, user_id, project_name, skill):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
        self.__executemany(sql, data)


    def get_statuses(self):
        sql = 'SELECT * FROM status'
        return self.__select_data(sql)
        

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None
    def get_project_info(self, user_id, project_name):
        """
        Возвращает детальную информацию о проекте (имя, описание, ссылку, статус)
        для конкретного пользователя.
        """
        # Используем JOIN и псевдонимы таблиц для ясности запроса
        sql = """
        SELECT p.project_name, p.description, p.url, s.status_name 
        FROM projects p 
        JOIN status s ON s.status_id = p.status_id 
        WHERE p.project_name = ? AND p.user_id = ?
        """
        return self.__select_data(sql, (project_name, user_id))
    def get_projects(self, user_id):
        sql = '''SELECT p.project_id, p.project_name, p.description, p.url , s.status_name
                FROM projects p
                JOIN status s ON s.status_id = p.status_id
                WHERE p.user_id = ?'''
        return self.__select_data(sql, (user_id,))
        
    def get_project_id(self, project_name, user_id):
        return self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?  ', data = (project_name, user_id,))[0][0]
        
    def get_skills(self):
        return self.__select_data(sql='SELECT * FROM skills')
    


    def get_project_skills(self, user_id, project_name):
        """
        Возвращает строку с навыками для конкретного проекта конкретного пользователя.
        """
        # Используем JOIN и псевдонимы таблиц для чистоты запроса
        sql = '''SELECT sk.skill_name 
                FROM projects p 
                JOIN project_skills ps ON p.project_id = ps.project_id 
                JOIN skills sk ON sk.skill_id = ps.skill_id 
                WHERE p.project_name = ? AND p.user_id = ?'''
        
        res = self.__select_data(sql, (project_name, user_id))
        
        # Если результат пустой, возвращаем понятное сообщение
        if not res:
            return "Нет навыков или проект не найден."
            
        # Собираем названия навыков в одну строку через запятую
        return ', '.join([x[0] for x in res])
    def get_project_info(self, user_id, project_name):
        sql = """
SELECT project_name, description, url, status_name FROM projects 
JOIN status ON
status.status_id = projects.status_id
WHERE project_name=? AND user_id=?
"""
        return self.__select_data(sql=sql, data = (project_name, user_id))


    def update_projects(self, param, data):
        sql = 'UPDATE projects SET status_id = ? Where projects_id =?'
        self.__executemany(sql, [data]) 


    def delete_project(self, user_id, project_id):
        sql = 'DELETE FROM projects WHERE user_id = ? AND  projects_id = ?'
        self.__executemany(sql, [(user_id, project_id)])
    
    def delete_skill(self, project_id, skill_id):
        sql = 'DELETE FROM projects_skills WHERE projects_id =? AND skills_id =? '
        self.__executemany(sql, [(skill_id, project_id)])

    def delete_status(self, startus_id):
        sql = 'DELETE FROM status WHERE status_id = ?'
        self.__executemany(sql,[(startus_id)])
    def  update_skill(self, skill_id, new_skill_name ):
        sql = 'UPDATE skills SET skill_name = ? Where skil_id =?'
        self.__executemany(sql, [(new_skill_name, skill_id)])
    def add_new_skill(self, skill_name):
        sql = 'INSERT ORIGNORE INTO skills (skill_name) VALUES (?)'
        self.__executemany(sql,[(skill_name)])
    def update_project_status(self, project_id, new_status_id):
        sql= 'UPDATE projects SET status_id = ? WHERE project_id = ? ' 
        self.__executemany(sql,[(new_status_id, project_id)])  
    def delete_project_skill_by_id(self, project_id, skill_id):
        sql = 'DELETE FROM project_skills WHERE project_id = ? AND skill_id = ?'
        self.__executemany(sql, [(project_id, skill_id)])

    def delete_all_project_skills(self, project_id):
        sql = 'DELETE FROM project_skills WHERE project_id = ?'
        self.__executemany(sql, [(project_id,)])
    def delete_skill_by_id(self, skill_id):
        sql = 'DELETE FROM skills WHERE skill_id = ?'
        self.__executemany(sql, [(skill_id,)])
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
#manager.create_tables()

data = [
    ('12345', 'Калькулятор ', 'калькулятор в тг боте', 'http://example.com', '1')
]

# Подключение к базе данных
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()
table_name="skills"

# Название нового столбца и его тип данных
new_column_name = 'image skill'
new_column_type = 'TEXT'

# Выполнение запроса на добавление столбца
#alter_query = f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} {new_column_type}"
#cursor.execute(alter_query)

# Сохранение изменений и закрытие соединения
#conn.commit()
#conn.close()
