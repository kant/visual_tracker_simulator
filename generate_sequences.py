from random import uniform, randrange

target_objects_in_scene = ["_none_", "Chevrolet", "Nissan"]

print("How many sequences do you want to generate?")
number_of_sequences = int(input())

print("How long at most do you want your sequences to be (in seconds)? Minimum is 17s.");
input_number = float(input())
if input_number < 17:
    input_number = 17

for i in range(number_of_sequences):
    # Preparation of some variables
    if uniform(0,10) > 8:
        fog = "True"
    else:
        fog = "False"

    number_of_frames = int(uniform(17, input_number) * 24)

    # Creating the txt file
    f = open("corvette/scene"+str(i)+".txt", "w")
    f.write("camera " + str(uniform(-10,10)) + " " + str(uniform(-10,10)) + " " + str(uniform(1,10)) + " " + str(uniform(0,180)) + " " + str(0) + " " + str(uniform(-180,180)) +  " \n")
    f.write("vehicle_density " + str(int(uniform(0,10))) + " \n")
    f.write("light " + str(uniform(-90,90)) + " " + str(uniform(-90,90)) + " " + str(uniform(-180,180)) + " \n")
    f.write("child_of " + target_objects_in_scene[randrange(len(target_objects_in_scene))] + " \n")
    f.write("fog " + fog + " \n")
    f.write("animation_length " + str(number_of_frames) + " \n")
    f.close()