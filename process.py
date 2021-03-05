import toml

filename = "data.toml"

with open(filename, "r") as f:
    data_bytes = f.read()


data = toml.loads(data_bytes)
print(data)

with open(filename, "w") as f:
    f.write(toml.dumps(data))
