from __future__ import print_function
from six.moves import xrange
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from database import db_session, GlobalVariables

#speed = 20
#dayLength = 40

###########################
# Problem Data Definition #
###########################
def create_data_model(_locations):
    # store problem data here
    data = {}
    # convert latitude and longitude degrees to miles
    #data["locations"] = [(l[0] * 69, l[1] * 69) for l in _locations]
    depot = 0
    #formattedLocations = [(l[0] * 69, l[1] * 69) for l in _locations]
    #formattedLocations = _locations
    #for i in range(len(_locations)):
    #    formattedLocations[i][0] = formattedLocations[i][0] * 69
    #    formattedLocations[i][1] = formattedLocations[i][1] * 69
    num_locations = len(_locations)
    dist_matrix = {}
    for from_node in range(num_locations):
        dist_matrix[from_node] = {}
        for to_node in range(num_locations):
            if(from_node == depot or to_node == depot):
                dist_matrix[from_node][to_node] = 0
            else:
                dist_matrix[from_node][to_node] = (manhattan_distance(_locations[from_node], _locations[to_node]))



    #data["num_locations"] = len(data["locations"])
    num_vehicles = 1
    # specifiy starting location
    #data["depot"] = 0
    return [num_vehicles, depot, _locations, dist_matrix]
#######################
# Problem Constraints #
#######################
def manhattan_distance(position_1, position_2):
    # Computes the Manhattan distance between two points
    return (abs(position_1[0] - position_2[0]) + abs(position_1[1] - position_2[1]))
def CreateDistanceCallback(dist_matrix):
    def dist_callback(from_node, to_node):
        return dist_matrix[from_node][to_node]
    return dist_callback
def create_distance_callback(data):
    # Creates callback to return distance between points
    _distances = {}
    for from_node in xrange(data["num_locations"]):
        _distances[from_node] = {}
        for to_node in xrange(data["num_locations"]):
            if from_node == to_node:
                _distances[from_node][to_node] = 0
            else:
                _distances[from_node][to_node] = (manhattan_distance(data["locations"][from_node], data["locations"][to_node]))

    def distance_callback(from_node, to_node):
        # Returns the manhattan distance between the two nodes
        return _distances[from_node][to_node]
    
    return distance_callback
def add_distance_dimension(routing, distance_callback):
    # Add Global Span constraint
    distance = 'Distance'
    maximum_distance = 9999999999  # Maximum distance per vehicle.
    routing.AddDimension(distance_callback, 0, maximum_distance, True, distance)
    distance_dimension = routing.GetDimensionOrDie(distance)
    # Try to minimize the max distance among vehicles.
    distance_dimension.SetGlobalSpanCostCoefficient(100)

# printing function used for testing
def print_solution(data, routing, assignment):
    # Print route on console
    total_distance = 0
    for vehicle_id in xrange(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} ->'.format(routing.IndexToNode(index))
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        plan_output += ' {}\n'.format(routing.IndexToNode(index))
        plan_output += 'Distance of route: {}m\n'.format(distance)
        print(plan_output)
        total_distance += distance
    print('Total distance of all routes: {}m'.format(total_distance))

# assignment creation function
def makeAssign(locations, duration):
    #formattedLocations = [(l[0] * 69, l[1] * 69) for l in locations]
    assignmentCollection = []
    vehicle_id = 0
    globalVar = db_session.query(GlobalVariables).first()
    speed = globalVar.averageSpeed
    dayLength = globalVar.workDayLength
    

    # Instantiate the data problem.
    while(len(locations) > 1):
        formattedLocations = [(l[0] * 69, l[1] * 69) for l in locations]
        #data = create_data_model(locations)
        [num_vehicles, depot, loca, dist_matrix] = create_data_model(formattedLocations)
        num_locations = len(formattedLocations)
        routing = pywrapcp.RoutingModel(num_locations, num_vehicles, depot)
        dist_callback = CreateDistanceCallback(dist_matrix)
        routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
        add_distance_dimension(routing, dist_callback)
        search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        assignment = routing.SolveWithParameters(search_parameters)



        time = duration
        distance = 0
        #vehicle_id = data["num_vehicles"][0]
        locs = []
        index = routing.Start(0)
        node = routing.IndexToNode(index)
        next_node = routing.IndexToNode(assignment.Value(routing.NextVar(index)))
        index = routing.NodeToIndex(next_node)
        node = routing.IndexToNode(index)
        next_node = routing.IndexToNode(assignment.Value(routing.NextVar(index)))

        # inspect the solution to the location order
        while not routing.IsEnd(index):
            node = routing.IndexToNode(index)
            next_node = routing.IndexToNode(assignment.Value(routing.NextVar(index)))
            distance = manhattan_distance(formattedLocations[node], formattedLocations[next_node])
            time = time + (distance/speed) + duration
            index = assignment.Value(routing.NextVar(index))

            locs.append(routing.IndexToNode(node))
            # if day length is exceeded don't add another location to the assignment
            if(time >= dayLength):
                break
            #previous_index = index
            #index = assignment.Value(routing.NextVar(index))
            # get distance between two locations
            #distance = routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            # calculate total time used for that day so far
            #time = time + (distance/speed) + duration
        
        # remove used locations from the data set before the next mapping iteration
        locElements = []
        for x in range(len(locs)):
            locElements.append(locations[locs[x]])
        assignmentCollection.append(locElements)
        for x in range(len(locElements)): 
            locations.remove(locElements[x])
    
    return assignmentCollection

#main function used for testing
def main():
    locations = \
               [(4,4),
                (2,0), (8,0),
                (6,1), (3,0),
                (5,2), (7,2)]
    duration = 20
    assn = makeAssign(locations, duration)
    print(assn)
if __name__ == '__main__':
    main()
