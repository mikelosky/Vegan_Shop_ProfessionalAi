from tinydb import TinyDB, Query
import json
import time
import os


class Database():
    """
    Class for managing database created using json files TinyDB is a lightweight library for database management in
    Python. It provides a simple and easy to use for storing data in a JSON database. The main functions of TinyDB
    include creating and database management, adding, editing and deleting data, and querying and accessing data
    stored. It is designed to be easy to integrate into Python projects due to its simplicity and lightness,
    especially suitable for applications that require basic database operations of a limited size.
    """

    def __init__(self):
        """
        Class initialization and file creation for Database
        """
        if not os.path.exists("./db"):
            os.mkdir("./db")
        if not os.path.exists("./db/prodotti.json"):
            file_product = open('./db/prodotti.json', 'w')
            file_product.close()
        if not os.path.exists("./db/conti.json"):
            file_count = open('./db/conti.json', 'w')
            file_count.write(json.dumps({"lordo": 0, "netto": 0}))
            file_count.close()
        self.all_products = Query()
        self.db = TinyDB("./db/prodotti.json")

    def insert_products(self, list_of_product, operation):
        """
        Function for entering new products or updating quantities of those already present
        """
        for product in list_of_product:
            query_res = self.db.search(self.all_products.name == product["name"])
            if query_res:
                if operation == "add":
                    new_count = query_res[0]["count"] + product["count"]
                elif operation == "sub":
                    new_count = query_res[0]["count"] - product["count"]
                self.db.update({'count': new_count}, self.all_products.name == product["name"])
            else:
                self.db.insert(product)

    def get_product(self, product_name):
        """
        Function retrieve a product from the Database
        """
        return self.db.search(self.all_products.name == product_name)

    def get_all_products(self):
        """
        Function to retrieve all elements in the db
        """
        return self.db.all()


class InvalidNegativeException(Exception):
    """
    Defining a class for a custom exception for detection applied when negative values are found
    """
    pass


class Product_Management(Database):
    """
    Class for managing the entry and sale of products that inherits the class for managing the Database
    """

    def start_managing(self):
        """
        Dedicated function for receiving user input
        """
        while True:
            main_input = input("Inserisci un comando: ")
            if main_input.lower() in ["aggiungi", "elenca", "vendita", "profitti", "aiuto", "chiudi"]:
                if main_input.lower() == "aggiungi":
                    product_name = input("Nome del prodotto: ").capitalize()
                    while True:
                        try:
                            product_quantity = int(input("Quantità: "))
                            if product_quantity < 0:
                                raise InvalidNegativeException
                        except ValueError:
                            print("Inserimento invalido! \nRiprova... ")
                        except InvalidNegativeException:
                            print("Il valore non puo essere negativo! \nRiprova... ")
                        else:
                            break
                    if self.get_product(product_name):
                        print("Prodotto presente nel Db. \nAggiornamento quantita.")
                        self.insert_products([{"name": product_name, "count": product_quantity}], "add")
                    else:
                        while True:
                            try:
                                product_purchase = float(input("Prezzo di acquisto: "))
                                if product_purchase < 0:
                                    raise InvalidNegativeException
                            except ValueError:
                                print("Inserimento invalido! \nRiprova... ")
                            except InvalidNegativeException:
                                print("Il valore non puo essere negativo! \nRiprova... ")
                            else:
                                break
                        while True:
                            try:
                                product_sale = float(input("Prezzo di vendita: "))
                                if product_sale < 0:
                                    raise InvalidNegativeException
                            except ValueError:
                                print("Inserimento invalido! \nRiprova... ")
                            except InvalidNegativeException:
                                print("Il valore non puo essere negativo! \nRiprova... ")
                            else:
                                break
                        self.insert_products([
                            {"name": product_name,
                             "count": product_quantity,
                             "buy_price": product_purchase,
                             "sell_price": product_sale
                             }]
                            , "add")
                    print(f"AGGIUNTO : {product_quantity} x {product_name}")
                elif main_input.lower() == "elenca":
                    all_products = self.get_all_products()
                    print("{:<5} {:<15} {:<8} {:<10}".format('IND.', 'PRODOTTO', 'QUANTITA', 'PREZZO'))
                    for index, product in enumerate(all_products):
                        print("{:<5} {:<15} {:<8} {:<10}".format(index, product["name"], product["count"],
                                                                 product["sell_price"]))
                elif main_input.lower() == "vendita":
                    sells = []
                    gross_value_sells = 0
                    while True:
                        product_name = input("Nome del prodotto: ").capitalize()
                        product = self.get_product(product_name)
                        if product:
                            product = product[0]
                            while True:
                                try:
                                    product_sell = int(input("Quantità: "))
                                    if product_sell >= product["count"]:
                                        raise IndexError()
                                    elif product_sell < 0:
                                        raise InvalidNegativeException
                                except ValueError:
                                    print("Inserimento invalido! \nRiprova... ")
                                except IndexError:
                                    print("Quantita non sufficiente! \nRiprova... ")
                                except InvalidNegativeException:
                                    print("Il valore non puo essere negativo! \nRiprova... ")
                                else:
                                    break

                            self.insert_products([{
                                "name": product["name"],
                                "count": product_sell,
                            }], "sub")
                            file_count = open('./db/conti.json', 'r')
                            data_count = json.load(file_count)
                            gross_value = (product_sell * product["sell_price"]) + data_count["lordo"]
                            net_value = ((product_sell * product["sell_price"]) - (
                                    product_sell * product["buy_price"])) + data_count["netto"]
                            file_count.close()
                            new_data_count = json.dumps({"lordo": round(gross_value, 2), "netto": round(net_value, 2)})
                            file_count_write = open('./db/conti.json', 'w')
                            file_count_write.write(new_data_count)
                            file_count_write.close()
                            sells.append([product_sell, product["name"], product["sell_price"]])
                            gross_value_sells += (product_sell * product["sell_price"])
                            while True:
                                answer = input("Aggiungere un altro prodotto ? (si/no): ").lower()
                                if answer in ["si", "no"]:
                                    break
                                else:
                                    print("Inserimento invalido! \nRiprova... ")
                            if answer == "no":
                                print("VENDITA REGISTRATA")
                                for s in sells:
                                    print(f"{s[0]} x {s[1]}: € {s[2]}")
                                print(f"Totale: {round(gross_value_sells, 2)}")
                                break
                        else:
                            print("Prodotto non presente! \nRiprova... ")
                elif main_input.lower() == "profitti":
                    file_count = open('./db/conti.json', 'r')
                    data_count = json.load(file_count)
                    file_count.close()
                    print(f"Profitto: lordo=€ {data_count['lordo']} netto=€ {data_count['netto']}")
                elif main_input.lower() == "aiuto":
                    print("{:<8} {:<50}".format('COMANDO', 'DESCRIZIONE'))
                    print("{:<8} {:<50}".format('aggiungi', 'aggiungi un prodotto al magazzino'))
                    print("{:<8} {:<50}".format('elenca', 'elenca i prodotto in magazzino'))
                    print("{:<8} {:<50}".format('vendita', 'registra una vendita effettuata'))
                    print("{:<8} {:<50}".format('profitti', 'mostra i profitti totali'))
                    print("{:<8} {:<50}".format('aiuto', 'mostra i possibili comandi'))
                    print("{:<8} {:<50}".format('chiudi', 'esci dal programma'))
                elif main_input.lower() == "chiudi":
                    print("Bye bye")
                    break
            else:
                print("Comando non presente! \nPer avere l`elenco dei comandi disponibili inserire ===> aiuto")
                time.sleep(2)


if __name__ == "__main__":
    pm = Product_Management()
    pm.start_managing()
