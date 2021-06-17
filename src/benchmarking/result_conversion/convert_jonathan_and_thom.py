import os


def parse_file(input_file):
    with open(os.path.join(map_root, input_file)) as f:
        lines = f.readlines()
    filename = input_file.split(".")
    filename = filename[0].split("-")
    name = filename[0].strip()
    teams = filename[1].strip()
    with open(output_file, 'a') as f:
        for line in lines:
            split_line = line.split(":")
            agents = split_line[0].strip()
            array = split_line[1].strip()[1:-1]
            folder = f"{name}-20x20-A{agents}_T{teams}"
            for index, time in enumerate(array.split(",")):
                padded_index = str(index)
                if index < 10:
                    padded_index = "0" + padded_index
                if index < 100:
                    padded_index = "0" + padded_index
                f.write(f"{folder}, {folder}-{padded_index}.map, {time.strip()}\n")


if __name__ == "__main__":
    map_root = "../../../results/others/Thom"
    output_file = "../../../results/others/Thom.txt"
    for path in os.listdir(map_root):
        parse_file(path)
