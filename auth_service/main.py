from concurrent import futures
import grpc
import auth_pb2
import auth_pb2_grpc
from confluent_kafka import Producer
import json
from command_handler import UserCommandHandler
from query_handler import UserQueryHandler

# Configurazione del Producer Kafka
kafka_config = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'auth-service-producer'
}
producer = Producer(kafka_config)

# Funzione per inviare eventi Kafka
def send_event_to_kafka(event_type, payload):
    topic = "user-events"
    message = {"type": event_type, **payload}
    producer.produce(topic, key=payload.get("email", ""), value=json.dumps(message), callback=delivery_report)
    producer.flush()

# Callback per la verifica della consegna
def delivery_report(err, msg):
    if err is not None:
        print(f"Errore nell'invio del messaggio Kafka: {err}")
    else:
        print(f"Messaggio inviato al topic {msg.topic()} - Chiave: {msg.key()} - Valore: {msg.value()}")

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        self.command_handler = UserCommandHandler()
        self.query_handler = UserQueryHandler()

    def RegisterUser(self, request, context):
        """
        Registra un nuovo utente con soglie e (opzionalmente) un ticker.
        """
        try:
            # Verifica se l'utente esiste già
            user = self.query_handler.get_user_by_email(request.email)
            if user:
                user_id = user['id']
            else:
                # Crea un nuovo utente
                user_id = self.command_handler.create_user(request.email, request.high_value, request.low_value)
                send_event_to_kafka("UserRegistered", {
                    "email": request.email,
                    "high_value": request.high_value,
                    "low_value": request.low_value
                })
                print(f"Utente {request.email} registrato con ID {user_id}")

            # Aggiungi un ticker se fornito
            if request.ticker:
                existing_ticker = self.query_handler.get_ticker_for_user(user_id, request.ticker)
                if existing_ticker:
                    return auth_pb2.AuthUserResponse(status="Ticker already exists for user")
                self.command_handler.add_ticker(user_id, request.ticker)
                send_event_to_kafka("TickerRegistered", {"email": request.email, "ticker": request.ticker})
                print(f"Ticker {request.ticker} associato all'utente {request.email}")

            return auth_pb2.AuthUserResponse(status="User and ticker registered successfully")
        except Exception as e:
            print(f"Errore durante la registrazione dell'utente: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.AuthUserResponse(status="Internal server error")

    def UpdateUser(self, request, context):
        """
        Aggiorna il ticker o le soglie di un utente.
        """
        try:
            # Recupera l'utente
            user = self.query_handler.get_user_by_email(request.email)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return auth_pb2.AuthUserResponse(status="User not found")
            user_id = user['id']

            # Aggiorna il ticker se richiesto
            if request.old_ticker and request.new_ticker:
                old_ticker_exists = self.query_handler.get_ticker_for_user(user_id, request.old_ticker)
                if not old_ticker_exists:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    return auth_pb2.AuthUserResponse(status="Old ticker not found")
                self.command_handler.update_ticker(user_id, request.old_ticker, request.new_ticker)
                send_event_to_kafka("TickerUpdated", {
                    "email": request.email,
                    "old_ticker": request.old_ticker,
                    "new_ticker": request.new_ticker
                })
                print(f"Ticker aggiornato per utente {request.email}: {request.old_ticker} -> {request.new_ticker}")

            # Aggiorna le soglie se richiesto
            if request.high_value or request.low_value:
                self.command_handler.update_thresholds(user_id, request.high_value, request.low_value)
                send_event_to_kafka("ThresholdsUpdated", {
                    "email": request.email,
                    "high_value": request.high_value,
                    "low_value": request.low_value
                })
                print(f"Soglie aggiornate per utente {request.email}: High={request.high_value}, Low={request.low_value}")

            return auth_pb2.AuthUserResponse(status="User and thresholds updated successfully")
        except Exception as e:
            print(f"Errore durante l'aggiornamento dell'utente: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.AuthUserResponse(status="Internal server error")

    def UpdateThresholds(self, request, context):
        """
        Aggiorna le soglie di un utente.
        """
        try:
            # Recupera l'utente
            user = self.query_handler.get_user_by_email(request.email)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return auth_pb2.AuthUserResponse(status="User not found")
            user_id = user['id']

            # Aggiorna le soglie
            self.command_handler.update_thresholds(user_id, request.high_value, request.low_value)
            send_event_to_kafka("ThresholdsUpdated", {
                "email": request.email,
                "high_value": request.high_value,
                "low_value": request.low_value
            })
            print(f"Soglie aggiornate per utente {request.email}: High={request.high_value}, Low={request.low_value}")

            return auth_pb2.AuthUserResponse(status="Thresholds updated successfully")
        except Exception as e:
            print(f"Errore durante l'aggiornamento delle soglie: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.AuthUserResponse(status="Internal server error")

    def DeleteUser(self, request, context):
        """
        Elimina un utente o un ticker associato.
        """
        try:
            # Recupera l'utente
            user = self.query_handler.get_user_by_email(request.email)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return auth_pb2.AuthUserResponse(status="User not found")
            user_id = user['id']

            # Elimina un ticker specifico o tutto l'utente
            if request.ticker:
                self.command_handler.delete_ticker(user_id, request.ticker)
                send_event_to_kafka("TickerDeleted", {"email": request.email, "ticker": request.ticker})
                print(f"Ticker {request.ticker} eliminato per utente {request.email}")
                return auth_pb2.AuthUserResponse(status="Ticker deleted successfully")
            else:
                self.command_handler.delete_user(user_id)
                send_event_to_kafka("UserDeleted", {"email": request.email})
                print(f"Utente {request.email} eliminato con tutti i suoi ticker")
                return auth_pb2.AuthUserResponse(status="User and associated tickers deleted successfully")
        except Exception as e:
            print(f"Errore durante l'eliminazione dell'utente: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.AuthUserResponse(status="Internal server error")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('0.0.0.0:5001')
    server.start()
    print("AuthService in esecuzione sulla porta 5001...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()