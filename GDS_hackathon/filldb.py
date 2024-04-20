import psycopg
from helpers.openai import send_embedding
from config import DB_URL

conn = psycopg.connect(DB_URL)
cursor = conn.cursor()


def store(part, embedding_description, embedding_topic, table_name='info'):
    try:
        cursor.execute(f"""
            INSERT INTO {table_name} (
                category, topic, description, embedding_description, embedding_topic
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            part['category'],
            part['topic'],
            part['description'],
            embedding_description,
            embedding_topic
        ))
        print(f'Successfully stored {part['topic']}')
        conn.commit()
    except Exception as error:
        print(f"Error storing part '{part['topic']}': {error}")
        return "ERROR"


def main():
    ls = list()
    with open('asdfasdf') as f:
        docs = ''.join(f.readlines()).split(10 * '~')
    for part in docs:
        part = part.strip()
        title, desc = part.split(5 * "~")
        title = title.strip().strip("#")
        category, topic = (title.split(" = "))
        ls.append({'category': category, 'topic': topic, 'description': desc})

    for hmap in ls:
        if store(hmap, send_embedding(hmap['description'].strip()),
                 send_embedding(hmap['topic'].strip("#").strip()), table_name) == "ERROR":
            print("error")
            return


if __name__ == '__main__':
    main()
