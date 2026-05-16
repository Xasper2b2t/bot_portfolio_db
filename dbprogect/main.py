from logic import DB_Manager 
from config import DATABASE
#def main():
#    app = ConcoleProject
#    app.start()
#    def __init__(self, user_id= 1):
#        self.manager = DB_manager(DATABASE)
 #       self.user_id= user_id
 #       self.cansel_button = 





def print_menu():
    print("\n" + "="*40)
    print("КОНСОЛЬНОЕ ПРИЛОЖЕНИЕ ДЛЯ УПРАВЛЕНИЯ ПРОЕКТАМИ")
    print("="*40)
    print("1. Добавить новый проект")
    print("2. Добавить навык к проекту")
    print("3. Показать список моих проектов")
    print("4. Показать подробную информацию о проекте")
    print("5. Показать навыки проекта")
    print("6. Изменить статус проекта")
    print("7. Удалить проект")
    print("8. Выход")
    print("="*40)

def main():
    db = DB_Manager('my_database.db')
    db.create_tables()
    db.default_insert()

    while True:
        print_menu()
        
        choice = input("Выберите пункт меню: ").strip()
        
        if choice == '1':
            user_id = input("Введите User ID: ")
            name = input("Название проекта: ")
            desc = input("Описание: ")
            url = input("URL (если есть): ")
            
            # Показываем список статусов для выбора
            statuses = db.get_statuses()
            print("\nДоступные статусы:")
            for i, st in enumerate(statuses):
                print(f"{i+1}. {st[1]}")
            
            try:
                num_status = int(input("Выберите номер статуса: "))
                if 1 <= num_status <= len(statuses):
                    status_id = statuses[num_status-1][0]
                    db.insert_project([(user_id, name, desc, url, status_id)])
                    print("\n✅ Проект успешно добавлен!")
                else:
                    print("❌ Неверный номер статуса.")
            except ValueError:
                print("❌ Номер статуса должен быть целым числом.")


        elif choice == '2':
            user_id = input("User ID: ")
            proj_name = input("Название проекта: ")
            
            # Проверяем существование проекта перед добавлением навыка
            info = db.get_project_info(user_id, proj_name)
            if not info:
                print(f"❌ Проект '{proj_name}' не найден для пользователя {user_id}.")
                continue

            # Показываем список навыков для выбора
            skills_list = db.get_skills()
            print("\nДоступные навыки:")
            for i, sk in enumerate(skills_list):
                print(f"{i+1}. {sk[1]}")
            
            try:
                num_skill = int(input("Выберите номер навыка: "))
                if 1 <= num_skill <= len(skills_list):
                    skill_name = skills_list[num_skill-1][1]
                    db.insert_skill(user_id, proj_name, skill_name)
                    print(f"\n✅ Навык '{skill_name}' добавлен к проекту.")
                else:
                    print("❌ Неверный номер навыка.")
            except ValueError:
                print("❌ Номер навыка должен быть целым числом.")


        elif choice == '3':
            user_id = input("Введите ваш User ID: ")
            projects = db.get_projects(user_id)
            
            if not projects:
                print("\n📭 У вас нет проектов.")
                continue

            print(f"\n📂 Проекты пользователя {user_id}:")
            for p in projects:
                # p[0]=id, p[1]=name, p[4]=status_name
                print(f"ID: {p[0]} | Название: {p[1]} | Статус: {p[4]}")


        elif choice == '4':
            user_id = input("User ID: ")
            name = input("Название проекта: ")
            
            info = db.get_project_info(user_id, name)
            if not info:
                print(f"❌ Проект '{name}' не найден.")
                continue

            p_name, desc, url, status = info[0]
            print(f"\n📄 ИНФОРМАЦИЯ О ПРОЕКТЕ")
            print(f"Название: {p_name}")
            print(f"Описание: {desc}")
            print(f"Ссылка: {url}")
            print(f"Статус: {status}")


        elif choice == '5':
            user_id = input("User ID: ")
            name = input("Название проекта: ")
            
            # Проверяем существование проекта через метод get_project_info (он вернет пустой список или данные)
            info = db.get_project_info(user_id, name)
            if not info:
                print(f"❌ Проект '{name}' не найден.")
                continue

            skills_str = db.get_project_skills(user_id, name)
            print(f"\n⚙️ Навыки проекта '{name}': {skills_str}")


        elif choice == '6':
            try:
                proj_id_str = input("Введите ID проекта: ")
                if not proj_id_str.isdigit():
                    raise ValueError("ID должен быть числом")
                
                proj_id = int(proj_id_str)
                
                statuses = db.get_statuses()
                print("\nДоступные статусы:")
                for i, st in enumerate(statuses):
                    print(f"{i+1}. {st[1]}")
                
                num_status_str = input("Выберите новый номер статуса: ")
                if not num_status_str.isdigit():
                    raise ValueError("Номер статуса должен быть числом")
                
                num_status = int(num_status_str)
                
                if 1 <= num_status <= len(statuses):
                    new_status_id = statuses[num_status-1][0]
                    db.update_project_status(proj_id, new_status_id)
                    print("\n🔄 Статус обновлен!")
                else:
                    print("\n❌ Неверный номер статуса.")
                    
            except ValueError as e:
                print(f"\n❌ Ошибка ввода: {e}")
            except IndexError:
                print("\n❌ Ошибка: Возможно, проект с таким ID не существует.")


        elif choice == '7':
            try:
                user_id = input("User ID: ")
                proj_id_str = input("ID проекта для удаления: ")
                
                if not proj_id_str.isdigit():
                    raise ValueError("ID должен быть числом")
                
                proj_id = int(proj_id_str)
                
                confirm = input(f"⚠️ Вы уверены? Удалить проект ID={proj_id}? (y/n): ")
                if confirm.lower() == 'y':
                    db.delete_project(user_id, proj_id)
                    # Удаляем связи с навыками после удаления самого проекта (на всякий случай)
                    db.delete_all_project_skills(proj_id)
                    print("\n🗑️ Проект удален.")
                else:
                    print("\n❌ Удаление отменено.")
                    
            except ValueError as e:
                print(f"\n❌ Ошибка ввода: {e}")
            except Exception as e:
                # Обработка случая "проект не найден"
                if "no such column" in str(e) or "no such table" in str(e):
                    print("\n❌ Ошибка базы данных. Проверьте структуру.")
                else:
                    print(f"\n❌ Неизвестная ошибка при удалении: {e}")


        elif choice == '8':
            print("\n👋 Завершение работы...")
            break

        else:
            print("\n⚠️ Неверный пункт меню. Попробуйте еще раз.")


if __name__ == '__main__':
#    manager = DB_Manager(DATABASE)
    main()