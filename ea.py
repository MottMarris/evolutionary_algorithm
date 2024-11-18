import random
import collections
import copy
random.seed()

def evaluate_fitness(board):
    # Calculates the number of duplicates in every row, column and 3x3 subgrid. If a duplicate is found,
    # 1 is added to the score. The lower the score, the better the fitness.
    score = 0

    # Generate a dictionary that counts the amount of each value in every row and return the values.
    # If the count is more than 1, append this to the list as this means there are duplicates. Subtract
    # one from this value so we do not overcalculate. For example, if the value 2 was seen twice in a row,
    # the count would be 2. However, this means there is only one duplicate, so we subtract 1 from the count.
    # Sum the array to find to the total number of duplicates and add it to the score.
    score += sum([value-1 for dict in [collections.Counter(row).values() for row in board] for \
    value in dict if value != 1])

    # Does the same as above expect first transposes the grid so that the rows become the columns. Allows
    # us to count the duplicates in every column with the same piece of code.
    transposed = [list(sublist) for sublist in list(zip(*board))]

    score += sum([value-1 for dict in [collections.Counter(row).values() for row in transposed] for \
    value in dict if value != 1])

    # Counts the number of duplicates in the 3x3 subgrids. Iterates through the subgrids and puts them into
    # row formart so we can resuse the code above.
    subgrids = []

    for i in range(0,9,3):
        for j in range(0,9,3):
            subgrid = []
            secTopX, secTopY = i, j
            for x in range(i, secTopX+3):
                for y in range(secTopY, secTopY+3):
                    subgrid.append(board[x][y])
            subgrids.append(subgrid)

    score += sum([value-1 for dict in [collections.Counter(row).values() for row in subgrids] for \
    value in dict if value != 1])

    return score

def column_duplicate(board, column, value):
    # Checks if a value is already in a column
    return value in [list(sublist) for sublist in list(zip(*board))][column]

def subgrid_duplicate(board, row, column, value):
    # Checks if a value is already in a subgrid.
    i = 3*(int(row/3))
    j = 3*(int(column/3))

    if((board[i][j] == value)
       or (board[i][j+1] == value)
       or (board[i][j+2] == value)
       or (board[i+1][j] == value)
       or (board[i+1][j+1] == value)
       or (board[i+1][j+2] == value)
       or (board[i+2][j] == value)
       or (board[i+2][j+1] == value)
       or (board[i+2][j+2] == value)):
        return True
    else:
        return False

def get_coordinates(board):
    # Returns the coordinates of all the empty squares on the board.
    return [(i,j) for  i in range(9) for j in range(9) if board[i][j] == 0]

def show_board(board):
    # Prints of a formatted Sudoku board.
    for i in range(9):
        line = "|"
        for j in range(9):
            if j in [0,3,6]:
                line = line + "" + str(board[i][j])
            else:
                line = line + "  " + str(board[i][j])
            if (j+1) % 3 == 0:
                line = line + "|"
        if (i) % 3 == 0:
            print("-------------------------")
        print(line)
    print("-------------------------")

def random_solution(board, coordinates):
    # Iterate through the empty squares on the board and replaces their values with a random number
    # between 1 and 9.
    for coordinate in coordinates:
        board[coordinate[0]][coordinate[1]] = random.randint(1,9)
    return board

def create_population(board, coordinates):
    # Create a copy of the board then turn it into a random solution. Do this for a number of iterations
    # equal to our population size.
    return [random_solution(copy.deepcopy(board), coordinates) for _ in range(POPULATION_SIZE)]

def survival(population):
    # Order the population by their fitness and then keep the best 40% of the population.
    return sorted(population, key=lambda board, : evaluate_fitness(board))[:int(POPULATION_SIZE * 0.4)]

def crossover_population(population, board, coordinates):
    # With the best 40% of the population, cross them over to create a number of children equal to the
    # population size.
    crossed_population = []
    for _ in range(POPULATION_SIZE):
        # Randomly select two boards from the population.
        board1, board2 = random.choice(population), random.choice(population)
        board_copy = copy.deepcopy(board)
        # Iterate through the copy of the original board and replaces the 0s with one of the two numbers
        # at this same position from one of the randomly selected boards.
        for coordinate in coordinates:
            i, j = coordinate[0], coordinate[1]
            board_copy[i][j] = random.choice((board1[i][j], board2[i][j]))
        crossed_population.append(board_copy)

    return crossed_population

def mutate_population(population, coordinates):
    # 10% chance of mutation.
    if random.random() < 0.1:
        selection = random.random()
        # 25% chance of randomly swapping two values in a row.
        if selection < 0.25:
            for board in population:
                # Try for 100 iterations only because it might be impossible.
                for i in range(100):
                    row = random.randint(0,8)
                    column_from = random.randint(0,8)
                    column_to = random.randint(0,8)
                    # If it's the same column, pick new coordinates.
                    if column_from == column_to:
                        continue
                    # If the selected coordinates are the coordinates of values that we cannot change, try again.
                    if (row, column_from) not in coordinates or (row, column_to) not in coordinates:
                        continue
                    from_value = board[row][column_from]
                    to_value = board[row][column_to]
                    # If swapping these numbers would create a duplicate in a column or subgrid, try again.
                    if column_duplicate(board, column_to, from_value) or column_duplicate(board, column_from, to_value) or \
                    subgrid_duplicate(board, row, column_to, from_value) or subgrid_duplicate(board, row, column_from, to_value):
                        continue
                    # Swap the numbers
                    board[row][column_from], board[row][column_to] = board[row][column_to], board[row][column_from]
                    break

        # 60% chance of selection. Go through every board and randomly choose 5 changeable squares and
        # change them to a random number between 1 and 9.
        if selection >=0.25 and selection <= 0.85:
            for board in population:
                for _ in range(5):
                    i, j = random.choice(coordinates)
                    board[i][i] = random.randint(1,9)

def evoltuonary_algorithm(board):

    coords = get_coordinates(board)
    pop = create_population(board,coords)
    no_change = 0
    prev_best = None

    # 10,000 iterations. If we can't find a solution in this time, return the original board.
    for i in range(10000):
        best_pop = survival(pop)
        pop = crossover_population(best_pop,board,coords)
        mutate_population(pop,coords)
        # Save the best board of this population.
        new_best_board = sorted(pop, key=lambda board: evaluate_fitness(board))[0]

        # If the best boards fitness is the same as the last best boards fitness, there was to improvement.
        # Note that there was no improvement for this generation.
        if evaluate_fitness(new_best_board) == prev_best:
            no_change += 1
        else:
            no_change = 0
        prev_best = evaluate_fitness(new_best_board)
        print(evaluate_fitness(new_best_board), i)

        # If there has been no change for 30 generations, the population has prematurely converged at
        # a suboptimal fitness level. Scrap the population and start again.
        if no_change == 30:
            pop = create_population(board, coords)
            no_change = 0

        # If the best boards fitness is 0, we have found a solution to the Sudoku and we return it.
        if evaluate_fitness(new_best_board) == 0:
            return new_best_board

    return board

grid1 = [[3,0,0,0,0,5,0,4,7],
         [0,0,6,0,4,2,0,0,1],
         [0,0,0,0,0,0,0,0,0],
         [0,5,0,0,1,6,0,0,2],
         [0,0,3,0,0,0,0,0,4],
         [8,1,0,0,0,0,7,0,0],
         [0,0,2,0,0,0,4,0,0],
         [5,6,0,8,7,0,1,0,0],
         [0,0,0,3,0,0,6,0,0]]

grid2 = [[0,0,2,0,0,0,6,3,4],
         [1,0,6,0,0,0,5,8,0],
         [0,0,7,3,0,0,2,9,0],
         [0,8,5,0,0,1,0,0,6],
         [0,0,0,7,5,0,0,2,3],
         [0,0,3,0,0,0,0,5,0],
         [3,1,4,0,0,2,0,0,0],
         [0,0,9,0,8,0,4,0,0],
         [7,2,0,0,4,0,0,0,9]]

grid3 = [[0,0,4,0,1,0,0,6,0],
         [9,0,0,0,0,0,0,3,0],
         [0,5,0,7,9,6,0,0,0],
         [0,0,2,5,0,4,9,0,0],
         [0,8,3,0,6,0,0,0,0],
         [0,0,0,0,0,0,6,0,7],
         [0,0,0,9,0,3,0,7,0],
         [0,0,0,0,0,0,0,0,0],
         [0,0,6,0,0,0,0,1,0]]



POPULATION_SIZE = 20000
# To use a different grid, select either grid 1, 2 or 3 and input this into the evoltuonary_algorithm
# function.
solution = evoltuonary_algorithm(grid1)
show_board(solution)




"Some other methods that I wrote to try and improve performance but didn't actually use in my algorithm"

def tournament_selection(population):
    new_population = []
    for i in range(int(POPULATION_SIZE * 0.5)):
        board1, board2 = random.choice(population), random.choice(population)
        if evaluate_fitness(board1) <= evaluate_fitness(board2):
            fit = board1
            weak = board2
        else:
            fit = board2
            weak = board1
        if random.random() < 0.85:
            new_population.append(fit)
        else:
            new_population.append(weak)

    return new_population

def roullete_selection(population):
    population = sorted(population, key=lambda board: evaluate_fitness(board), reverse=True)
    total_fitness = sum([evaluate_fitness(board) for board in population])
    relative_fitness = [evaluate_fitness(board)/total_fitness for board in population]
    probs = [sum(relative_fitness[:i+1]) for i in range(len(relative_fitness))]
    # print(pro)
    new_population = []
    for n in range(int(POPULATION_SIZE / 3)):
        r = random.random()
        for (i, individual) in enumerate(population):
            if r <= probs[i]:
                new_population.append(individual)
                break
    return new_population


def k_crossover(population):
    new_population = []

    for i in range(int(POPULATION_SIZE/2)):
        point1 = random.randint(0,5)
        point2 = random.randint(5,10)
        board1, board2 = random.choice(population), random.choice(population)
        board1[point1:point2], board2[point1:point2] = board2[point1:point2], board1[point1:point2]
        new_population.append(board1)
        new_population.append(board2)
    return new_population

def r_solution(board, coordinates):
    for coordinate in coordinates:
        success = False
        for i in range(1000):
            row, column = coordinate[0], coordinate[1]
            # print(row, column)
            value = random.randint(1,9)
            if column_duplicate(board, column, value):
                continue
            if subgrid_duplicate(board, row, column, value):
                continue
            board[row][column] = value
            success = True
            break
        if not success:
            board[coordinate[0]][coordinate[1]] = random.randint(1,9)
    return board
