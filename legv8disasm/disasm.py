import sys

if (len(sys.argv) != 2):
    sys.exit(1)

filename = sys.argv[1]

instructions = {
    '10001011000': {"name": "ADD", "format": "R", "output": "ADD rd, rn, rm"},
    '1001000100': {"name": "ADDI", "format": "I", "output": "ADDI rd, rn, imm"},
    '10001010000': {"name": "AND", "format": "R", "output": "AND rd, rn, rm"},
    '1001001000': {"name": "ANDI", "format": "I", "output": "ANDI rd, rn, imm"},
    '000101': {"name": "B", "format": "B", "output": "B address"},
    '01010100': {"name": "Bcond", "format": "CB", "output": "B.cond address"},
    '100101': {"name": "BL", "format": "B", "output": "BL address"},
    '11010110000': {"name": "BR", "format": "R", "output": "BR rn"},
    '10110101': {"name": "CBNZ", "format": "CB", "output": "CBNZ rt, address"},
    '10110100': {"name": "CBZ", "format": "CB", "output": "CBZ rt, address"},
    '11001010000': {"name": "EOR", "format": "R", "output": "EOR rd, rn, rm"},
    '1101001000': {"name": "EORI", "format": "I", "output": "EORI rd, rn, imm"},
    '11111000010': {"name": "LDUR", "format": "D", "output": "LDUR rd, [rn, address]"},
    '11010011011': {"name": "LSL", "format": "R", "output": "LSL rd, rn, rm"},
    '11010011010': {"name": "LSR", "format": "R", "output": "LSR rd, rn, rm"},
    '10101010000': {"name": "ORR", "format": "R", "output": "ORR rd, rn, rm"},
    '1011001000': {"name": "ORRI", "format": "I", "output": "ORRI rd, rn, imm"},
    '11111000000': {"name": "STUR", "format": "D", "output": "STUR rd, [rn, address]"},
    '11001011000': {"name": "SUB", "format": "R", "output": "SUB rd, rn, rm"},
    '1101000100': {"name": "SUBI", "format": "I", "output": "SUBI rd, rn, imm"},
    '1111000100': {"name": "SUBIS", "format": "I", "output": "SUBIS rd, rn, imm"},
    '11101011000': {"name": "SUBS", "format": "R", "output": "SUBS rd, rn, rm"},
    '10011011000': {"name": "MUL", "format": "R", "output": "MUL rd, rn, rm"},
    '11111111101': {"name": "PRNT", "format": "R", "output": "PRNT rd"},
    '11111111100': {"name": "PRNL", "format": "R", "output": "PRNL"},
    '11111111110': {"name": "DUMP", "format": "R", "output": "DUMP"},
    '11111111111': {"name": "HALT", "format": "R", "output": "HALT"},
}

instruction_formats = {
    'R': {'format': [[21, 0x7FF], [16, 0x1F], [10, 0x3F], [5, 0x1F], [0, 0x1F]],
          'elements': ['opcode', 'rm', 'shamt', 'rn', 'rd'],},
    'I': {'format': [[22, 0x3FF], [10, 0xFFF], [5, 0x1F], [0, 0x1F]],
          'elements': ['opcode', 'imm', 'rn', 'rd'],},
    'D': {'format': [[21, 0x7FF], [12, 0x1FF], [10, 0x3], [5, 0x1F], [0, 0x1F]],
          'elements': ['opcode', 'address', 'op', 'rn', 'rd'],},
    'B': {'format': [[26, 0x3F], [0, 0x3FFFFFF]],
          'elements': ['opcode', 'address'],},
    'CB': {'format': [[24, 0xFF], [5, 0x7FFFF], [0, 0x1F]],
           'elements': ['opcode', 'address', 'rt'],},
    'IW': {'format': [[21, 0x7FF], [5, 0xFFFF], [0, 0x1F]],
           'elements': ['opcode', 'imm', 'rd'],}
}

conditional_codes = {
    0b0000: 'EQ',
    0b0001: 'NE',
    0b0010: 'HS',
    0b0011: 'LO',
    0b0100: 'MI',
    0b0101: 'PL',
    0b0110: 'VS',
    0b0111: 'VC',
    0b1000: 'HI',
    0b1001: 'LS',
    0b1010: 'GE',
    0b1011: 'LT',
    0b1100: 'GT',
    0b1101: 'LE',
}

def binary_to_integer(binary_string):
    if (len(binary_string) <= 8):
        return int(binary_string, 2)
    elif (int(binary_string[0]) & 1) == 0:  
        return int(binary_string, 2)
    else: 
        ones_complement = ''.join(['1' if (int(bit) & 1) == 0 else '0' for bit in binary_string])
        twos_complement = bin(int(ones_complement, 2) + 1)[2:]
        decimal = int(twos_complement, 2)
        negative_integer = -decimal
        return negative_integer

def return_or_add_label(label):
    if (label in labels):
        return labels[label]
    else:
        labels[label] = "label_" + str(len(labels))
        return labels[label]

def parse_instruction(instruction, machine_code, instruction_number):
    instruction_format = instruction['format']
    instruction_breakdown = instruction_formats[instruction_format]['format']
    instruction_elements = instruction_formats[instruction_format]['elements']
    instruction_segment = {}
    instruction_output = instruction["output"]
    for (j, [shift, mask]) in enumerate(instruction_breakdown):
        key = instruction_elements[j]

        if shift == None:
            instruction_segment[key] = bin(int(machine_code, 2) & mask)
        else:
            instruction_segment[key] = bin(int(machine_code, 2) >> shift & mask)

        if (instruction['name'] == "Bcond" and (key == "rt" or key == "address")):

            if (key == "rt"):
                conditional_code = int(instruction_segment[key], 2)
                for (machine_code, name) in conditional_codes.items():
                    if (conditional_code ^ machine_code == 0):
                        output_value = name
                key = "cond"
            elif (key == "address"):
                label = return_or_add_label(instruction_number + binary_to_integer(instruction_segment[key][2:]))
                output_value = label

        elif (key == "imm" or instruction_format == "B" or instruction_format == "BL" or (instruction_format.startswith("CB") and key == "address") or (instruction["format"] == "D" and key == "address") or (instruction['name'] == 'LSL' and key == 'rm') or (instruction['name'] == 'LSR' and key == 'rm')):

            if ((instruction_format == "B" or instruction_format == "CB") and key == "address"):
                label = return_or_add_label(instruction_number + binary_to_integer(instruction_segment[key][2:]))
                output_value = label
            else:
                output_value = "#" + str(binary_to_integer(instruction_segment[key][2:]))

        else:
        
            register = int(instruction_segment[key], 2)
            if (register == 30):
                output_value = "LR"
            elif (register == 29):
                output_value = "FP"
            elif (register == 28):
                output_value = "SP"
            else:
                output_value = "X" + str(int(instruction_segment[key], 2))
        instruction_output = instruction_output.replace(key, output_value)
    return instruction_output

instruction_matches = [
    [0b000101, 0b100101],  
    [0b10110101, 0b10110100, 0b01010100],  
    [0b1001000100, 0b1011000100, 0b1001001000, 0b1111001000, 0b1110101000, 0b1101001000, 0b1011001000, 0b1101000100, 0b1111000100], 
]

instruction_keys = list(instructions.keys())

output_array = []
labels = {0: "label_0"}

file = open(filename, "rb")
data = file.read()
binary_machine_code = ''.join(format(byte, '08b') for byte in data)
binary_code_segment = [binary_machine_code[i:i+32] for i in range(0, len(binary_machine_code), 32)]
for (i, code) in enumerate(binary_code_segment):
    found_match = False

    for instruction_match in instruction_matches[0]:
        opcode_segment = int(code, 2) >> 26 & 0x3F
        if opcode_segment ^ instruction_match == 0:
            found_match = True
            key = format(instruction_match, '06b')
            output_array.append(parse_instruction(instructions[key], code, i))

    for instruction_match in instruction_matches[1]:
        opcode_segment = int(code, 2) >> 24 & 0xFF
        if opcode_segment ^ instruction_match == 0 and not found_match:
            key = format(instruction_match, '08b')
            output_array.append(parse_instruction(instructions[key], code, i))

    for instruction_match in instruction_matches[2]:
        opcode_segment = int(code, 2) >> 22 & 0x3FF
        if opcode_segment ^ instruction_match == 0 and not found_match:
            key = format(instruction_match, '010b')
            output_array.append(parse_instruction(instructions[key], code, i))

    for instruction_match in instruction_keys:
        opcode_segment = int(code, 2) >> 21 & 0x7FF
        if opcode_segment ^ int(instruction_match, 2) == 0 and not found_match:
            output_array.append(parse_instruction(instructions[instruction_match], code, i))
file.close()

offset = 0
for (label, name) in labels.items():
    output_array.insert(label + offset, name + ":")
    offset += 1

for line in output_array:
    print(line)