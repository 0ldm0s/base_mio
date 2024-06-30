# -*- coding: UTF-8 -*-
import grpc
import grpc_greeter.calculator_pb2 as calculator_pb2
import grpc_greeter.calculator_pb2_grpc as calculator_pb2_grpc


def run(num1, num2):
    with grpc.insecure_channel("unix:///tmp/test.sock") as channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)
        response = stub.Add(calculator_pb2.AddRequest(num1=num1, num2=num2))
    print(f"Result: {response.result}")


if __name__ == '__main__':
    # Get user Input
    num1 = int(input("Please input num1: "))
    num2 = int(input("Please input num2: "))
    run(num1, num2)
