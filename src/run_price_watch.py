import argparse
import json

from price_watch_service import CatalogOffer, InfraiClient, monitor_offer


def main() -> None:
    parser = argparse.ArgumentParser(description="Record one competitor streaming offer")
    parser.add_argument("title")
    parser.add_argument("competitor")
    parser.add_argument("price", type=float)
    parser.add_argument("previous_price", type=float)
    parser.add_argument("--collection", default="streaming-offers")
    args = parser.parse_args()
    result = monitor_offer(InfraiClient(), args.collection, CatalogOffer(args.title, args.competitor, args.price), args.previous_price)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
