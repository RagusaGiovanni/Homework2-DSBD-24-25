from concurrent import futures
import grpc
import stock_pb2
import stock_pb2_grpc
from query_handler import StockQueryHandler

# Configurazione del database
db_config = {
    'host': 'mysql_db',
    'user': 'root',
    'password': 'example',
    'database': 'finance_data'
}

class StockService(stock_pb2_grpc.StockServiceServicer):
    def __init__(self):
        self.query_handler = StockQueryHandler(db_config)

    def GetStock(self, request, context):
        try:
            # Recupera l'ID utente
            user = self.query_handler.get_user_id_by_email(request.email)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return stock_pb2.StockResponse(status="User not found")
            user_id = user[0]

            # Verifica se il ticker esiste
            ticker_exists = self.query_handler.check_ticker_exists_for_user(user_id, request.ticker)
            if not ticker_exists:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return stock_pb2.StockResponse(status="Ticker not found for this user")

            # Recupera il valore più recente del ticker
            latest_value = self.query_handler.get_latest_stock_value(request.ticker)
            if latest_value:
                return stock_pb2.StockResponse(status="Stock found", value=latest_value[0])
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return stock_pb2.StockResponse(status="Stock not found")
        except Exception as e:
            print(f"Errore durante GetStock: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return stock_pb2.StockResponse(status="Internal server error")

    def GetAverage(self, request, context):
        try:
            # Recupera l'ID utente
            user = self.query_handler.get_user_id_by_email(request.email)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return stock_pb2.AverageResponse(status="User not found")
            user_id = user[0]

            # Verifica se il ticker esiste
            ticker_exists = self.query_handler.check_ticker_exists_for_user(user_id, request.ticker)
            if not ticker_exists:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return stock_pb2.AverageResponse(status="Ticker not found for this user")

            # Calcola la media
            average_value = self.query_handler.calculate_average_stock_value(request.ticker, request.count)
            if average_value and average_value[0] is not None:
                return stock_pb2.AverageResponse(status="Average calculated", average=average_value[0])
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return stock_pb2.AverageResponse(status="Stock not found or insufficient data")
        except Exception as e:
            print(f"Errore durante GetAverage: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return stock_pb2.AverageResponse(status="Internal server error")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stock_pb2_grpc.add_StockServiceServicer_to_server(StockService(), server)
    server.add_insecure_port('0.0.0.0:5002')
    server.start()
    print("Stock Service running on port 5002")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()