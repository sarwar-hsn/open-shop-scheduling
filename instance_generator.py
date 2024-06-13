import numpy as np

def generator(seed, num_instances):
    a = 16807
    b = 127773
    c = 2836
    m = pow(2,31)-1
    values = np.zeros(num_instances)

    for i in range(num_instances):
        k = seed//b
        seed = a*(seed%b) - k*c
        if seed<0:
            seed += m
        values[i] = seed/m

    return values

def operation_times_generator(time_seed, n, m):
    values = generator(time_seed, n*m)
    values =  [int(1+value*99) for value in values]
    times = [[0 for _ in range(m)] for _ in range(n)]
    i=0
    j=0
    for k in range(n*m):
        i = k//m
        j= k%m
        times[i][j] = values[k]

    return times


  
def machine_operations_generator(machine_seed, n, m):
    machines = [[i for i in range(m)] for _ in range(n)]
    values = generator(machine_seed, n*m)
    v=0
    for i in range(n):
        for j in range(m):
            k = int(j+(m-j)*values[v])
            v+=1
            machines[i][j], machines[i][k] = machines[i][k], machines[i][j]

    return machines


def create_file(output_file, n, m, processing_times, ub, lb):
    if output_file is not None:
        with open(output_file, 'w') as f:
            line = str(n) + " " + str(m) + "\n"
            f.write(line)
            for i in range(n):
                line = ""
                for j in range(m):
                    line += str(processing_times[i][j]) + " "
                f.write(line + "\n")
            line = str(ub) + " " + str(lb) + "\n"
            f.write(line)
            

def get_processing_times(n, m, time_seed, machine_seed):
    machine_operations = machine_operations_generator(machine_seed, n, m)
    operation_times = operation_times_generator(time_seed, n, m)
    processing_times = [[0]*m for _ in range(n)]
    for i in range(n):
        machines = machine_operations[i]
        for j in range(m):
            processing_times[i][j] = operation_times[i][machines.index(j)]
        
    return processing_times

def generate_instances(data, n, m):

    for k in range(10):
        instance = data[k]
        output_file = "./tests/test{}{}{}".format(n,m,k)
        create_file(output_file, n ,m ,get_processing_times(n,m,instance[0], instance[1]), instance[2], instance[3])

four = [
    [1166510396, 164000672, 193, 186],
    [1624514147, 1076870026, 236, 229],
    [1116611914, 1729673136, 271, 262],
    [410579806, 1453014524, 250, 245],
    [1036100146, 375655500, 295, 287],
    [597897640, 322140729, 189, 185], 
    [1268670769, 556009645, 201, 197],
    [307928077, 421384574, 217, 212],
    [667545295, 485515899, 261, 258],
    [35780816, 492238933, 217, 213]   
]

five = [
    [527556884, 1343124817, 300, 295],
    [1046824493, 1973406531, 262, 255],
    [1165033492, 86711717, 328, 321],
    [476292817, 24463110, 310, 306], 
    [1181363416, 606981348, 329, 321],
    [897739730, 513119113, 312, 307],
    [577107303, 2046387124, 305, 298],
    [1714191910, 1928475945, 300, 292],
    [1813128617, 2091141708, 353, 349],
    [808919936, 183753764, 326, 321]
]

seven = [
    [1840686215, 1827454623, 438, 435],
    [1026771938, 1312166461, 449, 443],
    [609471574, 670843185, 479, 468],
    [1022295947, 398226875, 467, 463],
    [1513073047, 1250759651, 419, 416],
    [1612211197, 95606345, 460, 451],
    [435024109, 1118234860, 435, 422],
    [1760865440, 1099909092, 426, 424],
    [122574075, 10979313, 460, 458],
    [248031774, 1685251301, 400, 398]
]

fifteen = [ [1561423441,1787167667, 956, 937],
[204120997, 213027331, 957, 918],
[801158374, 1812110433, 899, 871],
[1502847623, 1527847153, 946, 934],
[282791231, 1855451778, 992, 946],
[1130361878, 849417380, 959, 933],
[379464508, 944419714, 931, 891],
[1760142791, 1955448160, 916, 893],
[1993140927, 179408412, 951, 899],
[1678386613, 1567160817, 935, 902]
]

generate_instances(four,n=4,m=4)
generate_instances(five,n=5,m=5)
generate_instances(seven,n=7,m=7)
generate_instances(fifteen,n=15,m=15)