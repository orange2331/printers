import mysql.connector
import pandas as pd
from mysql.connector import Error
import win32com.client as win32


def connect(database):
    """ Connect to MySQL database """
    try:
        if database.is_connected():
            print('Connected to MySQL database')

    except Error as e:
        print(e)


def get_query(string, sqlbase):
    cursor = sqlbase.cursor()
    cursor.execute(string)
    result = cursor.fetchall()
    return result


def send_to_mail(to, attach_place):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = to
    mail.Subject = 'Заказ картриджей'
    mail.Body = 'Message body'
    mail.HTMLBody = 'Таблица на заказ картриджей'
    attachment = attach_place
    mail.Attachments.Add(attachment)
    mail.Send()
    print('Отправлено')


def insert_in_db(elements, sqlbase):
    string = "INSERT INTO orders(order_date,item_qty,item_id) VALUES(NOW(),%s,%s)"
    cursor = sqlbase.cursor()
    cursor.executemany(string, elements)
    sqlbase.commit()


if __name__ == '__main__':
    db = mysql.connector.connect(host='172.16.111.150',
                                 database='print',
                                 user='root',
                                 password='',
                                 port='3306')
    connect(db)
    query = ('SELECT CEILING(COUNT(events.id)/3), consumables.name, printers.department FROM events\n'
             'JOIN consumables ON consumable_id=consumables.id\n'
             'JOIN printers ON printer_id=printers.id\n'
             'WHERE date > LAST_DAY(CURDATE()) + INTERVAL 1 DAY - INTERVAL 3 MONTH\n'
             'AND date < DATE_ADD(LAST_DAY(CURDATE()), INTERVAL 1 DAY)\n'
             'GROUP BY consumables.name, printers.department')

    query_order_db = ('SELECT CEILING(COUNT(events.id)/3), consumable_id FROM events\n'
                      'WHERE date > LAST_DAY(CURDATE()) + INTERVAL 1 DAY - INTERVAL 3 MONTH\n'
                      'AND date < DATE_ADD(LAST_DAY(CURDATE()), INTERVAL 1 DAY)\n'
                      'GROUP BY consumable_id')

    rows = get_query(query, db)
    data = pd.DataFrame(data=rows, columns=['Необходимо', 'Модель', 'Расположение'])
    order_for_db = get_query(query_order_db, db)
    insert_in_db(order_for_db, db)
    db.close()
    if db.is_connected():
        print('MySQL still connected')
    else:
        print('MySQL disconnected')
    order_for_excel = data.sort_values(by=['Расположение'])
    order_for_excel.to_excel('order.xlsx', sheet_name='sheet_1', index=False)
    # if input('Отправить на почту?(y/n)') == 'y':
    #     place = "C:/Users/a.teplitskiy/PycharmProjects/untitled/order.xlsx"
    #     send_to_mail(input('Кому?'), place)
    # else:
    #     print('Таблица создана и внесена в orders')