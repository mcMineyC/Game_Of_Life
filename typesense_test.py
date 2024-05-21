import typesense, json

client = typesense.Client({
    'nodes': [{
        'host': '192.168.30.36',
        'port': '8108',
        'protocol': 'http'
    }],
    'api_key': 'xyz123',
    'connection_timeout_seconds': 2
})
lexicon_schema = {
  'name': 'lexicon',
  'fields': [
    {'name': 'id', 'type': 'string', 'facet': True},
    {'name': 'hash', 'type': 'string'},
    {'name': 'name', 'type': 'string' },
  ],
}

# client.collections['lexicon'].delete()

try:
    client.collections.create(lexicon_schema)
except typesense.exceptions.ObjectAlreadyExists:
    print('Collection already exists, skipping creation')

lexi = open('lexicon.jsonl', 'r')
client.collections['lexicon'].documents.import_(lexi.read().encode('utf-8'), {'action': 'upsert'})
lexi.close()

new_num = client.collections['lexicon'].retrieve()['num_documents']

print("Lexicon imported with", new_num, "documents.")