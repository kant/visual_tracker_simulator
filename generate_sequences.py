from random import uniform, randrange

print("How many sequences do you want to generate?")
number_of_sequences = int(input())

print("How long at most do you want your sequences to be (in seconds)? Minimum is 17s.");
input_number = float(input())
if input_number < 17:
    input_number = 17

print("Any specific object you want to follow? If not, leave blank.")
input_following_object = input()

for i in range(number_of_sequences):
    # Preparation of some variables
    if uniform(0,10) > 8:
        fog = "True"
    else:
        fog = "False"

    #
    number_of_frames = int(uniform(17, input_number) * 24)

    # Light offset
    light_offset = int(uniform(0, 800))

    # Creating the txt file
    f = open("corvette/scene"+str(i)+".txt", "w")
    f.write("camera " + str(uniform(-10,10)) + " " + str(uniform(-10,10)) + " " + str(uniform(1,10)) + " " + str(uniform(0,180)) + " " + str(0) + " " + str(uniform(-180,180)) +  " \n")
    f.write("generate_density " + str(int(uniform(0,10))) + " \n")
    f.write("light " + str(uniform(0,90)) + " " + str(uniform(-90,90)) + " " + str(uniform(-180,180)) + " \n")
    if input_following_object != "":
        f.write("child_of " +  input_following_object + " \n")
    f.write("fog " + fog + " \n")
    f.write("animation_length " + str(number_of_frames) + " \n")
    f.write("light_offset " + str(light_offset) + " \n")
    f.close()