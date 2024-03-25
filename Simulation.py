RANDOM_SEED = 1
MEAN_ID_TIME = 0.75 #avg time to check ID (exponential distribution)
SCAN_PARAM = [0.5,1]
PASS_ARR = 0.02    
NUM_ID_CHECK = 10
NUM_SCAN = 20
SIMULATION_REPEAT = 30


class Airport(object):
    def __init__(self, 
                 env, 
                 num_id_check, 
                 num_scan,
                 mean_id_time, 
                 scan_param ):
        self.env = env
        self.IDcheck = simpy.Resource(env, num_id_check)
        self.Scan = simpy.Resource(env, num_scan )
        self.mean_id_time = mean_id_time
        self.scan_param = scan_param
        
    def check_passenger(self, passenger):
        rand_ID_time = random.expovariate(MEAN_ID_TIME)
        yield self.env.timeout(rand_ID_time)
        
    def scan_passenger(self, passenger):
        rand_scan_time = random.uniform(self.scan_param[0],self.scan_param[1])
        yield self.env.timeout(rand_scan_time)

wait_times = []

def go_through_scanner(env, passenger, airport):
    # passenger arrives
    arrival = env.now
    
    # goes through checker and scanner
    with airport.IDcheck.request() as checker_request:
        yield checker_request
        yield env.process(airport.check_passenger(passenger))
        
    with airport.Scan.request() as scanner_request:
        yield scanner_request
        yield env.process(airport.scan_passenger(passenger))
    
    # calc wait time
    wait_times.append(env.now-arrival)
    
    
def run_airport(env, 
                num_id_check,
                num_scan, 
                mean_id_time, 
                scan_param):
    airport = Airport(env,num_id_check, num_scan, mean_id_time, scan_param)
 
    for passenger in range(1):
        env.process(go_through_scanner(env,passenger,airport))
        
    while True:
        yield env.timeout(1/(random.expovariate(PASS_ARR)))
        
        passenger += 1
        env.process(go_through_scanner(env,passenger,airport))
        

def get_wait_time(num_id_check, num_scan):
    random.seed(1)

  # Run the simulation
    env = simpy.Environment()
    env.process(run_airport(env,
                            num_id_check,
                            num_scan,
                            MEAN_ID_TIME, 
                            SCAN_PARAM))
    env.run(until=720)
    
    return statistics.mean(wait_times)

# creating a list of 1-20 for each checker and scanner
checker_list = list(range(1,15))
scanner_list = list(range(1,15))

# for each number in checker list and scanner list, go through each possible combo and find avg wait time
# example would be (1,1), (1,2)....(19,19)
# for i in range(len(checker_list)):
#   for j in range(len(scanner_list)):
#     wait_times = []
#     if get_wait_time(checker_list[i],scanner_list[j]) <= 15.0:
#         print('AVG wait with ID queues:', checker_list[i], 'and scanners:', scanner_list[j], 'is:', get_wait_time(checker_list[i],scanner_list[j]))
        
for i in range(len(checker_list)):
    for j in range(len(scanner_list)):
        avg_wait_times = []
        for _ in range(SIMULATION_REPEAT):
            wait_times = []
            avg_wait_times.append(get_wait_time(checker_list[i], scanner_list[j]))
        avg_wait_time = statistics.mean(avg_wait_times)
        if avg_wait_time <= 15.0:
            print('AVG wait with ID queues:', checker_list[i], 'and scanners:', scanner_list[j], 'is:', avg_wait_time)