from confluent_kafka import Consumer, Producer
import json
import mysql.connector

# Configurazione Kafka
kafka_config_consumer = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'alert-system-group',
    'auto.offset.reset': 'earliest'
}

kafka_config_producer = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'alertsystem-producer'
}

consumer = Consumer(kafka_config_consumer)
producer = Producer(kafka_config_producer)

# Configurazione del database MySQL
db_config = {
    'host': 'mysql_db',
    'user': 'root',
    'password': 'example',
    'database': 'finance_data'
}

def get_user_thresholds_and_email(ticker):
    """
    Recupera le soglie (high_value, low_value) e l'email associata a un ticker dal database.
    """
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT u.email, u.high_value, u.low_value
            FROM users u
            JOIN user_tickers t ON u.id = t.user_id
            WHERE t.ticker = %s
        """, (ticker,))
        result = cursor.fetchone()
        if result:
            email, high_value, low_value = result
            return email, float(high_value), float(low_value)
        return None, None, None
    finally:
        cursor.close()
        connection.close()

def process_stock_update(message):
    """
    Elabora i messaggi ricevuti dal topic 'to-alert-system'.
    Verifica se il valore supera le soglie e invia un evento al topic 'to-notifier'.
    """
    try:
        # Decodifica il messaggio ricevuto
        data = json.loads(message.value().decode('utf-8'))
        print(f"Messaggio ricevuto: {data}")

        ticker = data.get('ticker')
        value = float(data.get('value', 0))

        # Recupera soglie ed email dal database
        email, high_value, low_value = get_user_thresholds_and_email(ticker)
        if email is None:
            print(f"Nessuna email o soglie trovate per il ticker {ticker}")
            return

        # Mappa delle condizioni leggibili
        condition_map = {
            "HIGH_THRESHOLD_EXCEEDED": "Superamento della soglia superiore",
            "LOW_THRESHOLD_EXCEEDED": "Superamento della soglia inferiore"
        }

        # Controllo superamento soglie
        if value > high_value:
            condition = "HIGH_THRESHOLD_EXCEEDED"
            readable_condition = condition_map[condition]
            print(f"{ticker} ha superato la soglia alta: {value} > {high_value}")
            send_alert_to_notifier(email, ticker, readable_condition)

        elif value < low_value:
            condition = "LOW_THRESHOLD_EXCEEDED"
            readable_condition = condition_map[condition]
            print(f"{ticker} ha superato la soglia bassa: {value} < {low_value}")
            send_alert_to_notifier(email, ticker, readable_condition)

    except Exception as e:
        print(f"Errore nell'elaborazione del messaggio: {e}")

def send_alert_to_notifier(email, ticker, readable_condition):
    """
    Invia un messaggio Kafka al topic 'to-notifier' con i dettagli dell'alert.
    """
    alert_message = {
        "type": "Alert",
        "email": email,
        "ticker": ticker,
        "condition": readable_condition  # Tradotto in linguaggio leggibile
    }

    producer.produce("to-notifier", key=ticker, value=json.dumps(alert_message))
    producer.flush()
    print(f"Messaggio di alert inviato: {alert_message}")

def consume_alerts():
    """
    Consuma messaggi dal topic 'to-alert-system' e li elabora.
    """
    consumer.subscribe(['to-alert-system'])

    print("In ascolto sul topic 'to-alert-system'...")
    try:
        while True:
            msg = consumer.poll(1.0)  # Attende messaggi per 1 secondo
            if msg is None:
                continue
            if msg.error():
                print(f"Errore nel messaggio Kafka: {msg.error()}")
                continue

            # Elabora il messaggio ricevuto
            process_stock_update(msg)

    except KeyboardInterrupt:
        print("Chiusura del consumer Kafka...")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_alerts()