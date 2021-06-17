import os


def parse_file(input_file):
    with open(os.path.join(map_root, input_file)) as f:
        lines = f.readlines()
    filename = input_file.split("_")
    name = '_'.join((filename[1], filename[2]))
    with open(output_file, 'a') as f:
        for line in lines:
            data = line.split(",")
            f.write(f"{name}, {data[0].strip()}, {data[1].strip() if data[1].strip() != '' else None}\n")


if __name__ == "__main__":
    map_root = "../../../results/others/Robbin"
    output_file = "../../../results/others/Robbin.txt"
    for path in os.listdir(map_root):
        parse_file(path)
