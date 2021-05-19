from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import ElasticacheForRedis
from diagrams.aws.network import APIGateway
from diagrams.aws.network import Route53
from diagrams.onprem.container import Docker

with Diagram("Nemo Web Service", show=False, direction="TB"):
    with Cluster("Frontend", direction="LR"):
        dns = Route53("DNS")
        frontend = EC2("Frontend")
        apig = APIGateway("API Gateway")
        dns >> frontend >> apig
    with Cluster("Backend", direction="LR"):
        api = EC2("Nemo API")
        redis = ElasticacheForRedis("Redis")
        api >> Edge() << redis
    with Cluster("Fishnet", direction="LR"):
        fishnet = [Docker("Fishnet1"),
                   Docker("Fishnet2"),
                   Docker("Fishnet3")]
        api >> fishnet
    apig >> api

