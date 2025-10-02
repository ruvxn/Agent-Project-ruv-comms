from src.memory.QdrantStore import QdrantStore




def main():
    store = QdrantStore(collection_name="WebAgent")
    memories = store.get("The user greeted with a simple 'Hello'.")
    print(memories)


if __name__ == "__main__":
    main()