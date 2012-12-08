//Formal definition of first part of tracking algorithm

//Type definitions:
Coords = int[2]
Event_type = {P, N}
Transition_type =  { PN, NP}

Event(float timestamp, Coords coordinates, Event_type event_type);

Transition(float timestamp, Coords coordinates, Transition_type transition_type);

Interval(float timestamp, Coords coordinates, float delta);    // half the period

Guess(float timestamp, float frequency, Coords coordinates, float score)


H = 128
W = 128

class Tracker {

    //methods
    Tracker(float[] frequencies, float frequency_sigma, float buffer_smooth_sigma,
        int nguesses, float min_distance) {
 
        for i in 0 ... nguesses-1:
            f = FrequencyAccumulator(frequencies[i], frequency_sigma, 
                                    buffer_smooth_sigma, nguesses,
                                    min_distance);
            this.frequency_accum[i] = f;


        // We keep track of the last event seen at each pixel.
        // At the beginning, the timestamp is initialized to 0, meaning 
        // no event has been observed.
        this.LastEvent = new Event[H][W];
        
        // We keep track of the last transitions, separately
        // for PN and NP transitions.
        this.LastTransitionPN = new Transition[H][W];
        this.LastTransitionNP = new Transition[H][W];
    }


    // Main function, event driven
    void ProcessEvent(Event){
        // See of this event generates a transition
        Transition = GetTransition(Event);
        
        // If not, don't do anything
        if(Transition == null)
            return;

        interval = GetInterval(Transition);
        if(interval == null)
            return;

        // first, we accumulate the contribution to each estimator
        for (frequency_accum in this.frequency_accum) 
            frequency_accum.ProcessInterval(interval);
        
        // Then we look at which estimators have exhausted their time slice
        for (frequency_accum in this.frequency_accum) 
            // when it does, we output the gueeses
            if frequency_accum.is_expired():
                guesses = frequency_accum.get_guesses();
                this.output_guesses(guesses)
    }

    void output_guesses(Guess[] guesses) {
        // output the guesses to a file

        // Format:
        //  timestamp(float)  id_track  num_hypothesis hyphotesis_index  x y score
        // For example, suppose you have 3 hypotheses for frequency 1000:
        // 0.001234   1000  3 0  10.0 11.0 100.12
        // 0.001234   1000  3 1  20.0 21.0 10.2
        // 0.001234   1000  3 2  50.0 11.0 1.0
    }

    Transition GetTransition(Event event){
        // Check the last event at the same coordinates
        Event last_event = LastEvent[event.coordinates];
        // Record this event
        LastEvent[event.coordinates] = event
        // Check that we already received an event for those coordinates
        last_event_valid = last_event.timestamp != 0
        // Check that it's a different type
        different_type = last_event.type != event.type
        if last_event_valid and different_type:
            // Generate a transition
            return Transition(event.timestamp, event.coordinates, event.type);
        else
            return null;
    }

    Interval GetInterval(Transition t){
        // Look at which transition map we should update
        last_transition_map =  t.type == PN ? LastTransitionPN : LastTransitionNP;
        last_t = last_transition_map[t.coordinates]
        last_transition_map[t.coordinates] = t
        // Check that we already had a transition
        if last_t.timestamp == 0:
            return null;
        // Compute the interval
        float delta = t.timestamp - last_t.timestamp;
        return Interval(t.timestamp, t.coordinates, delta);
    }

};



class FrequencyAccumulator() {
     
    FrequencyAccumulator(float frequency, float frequency_sigma, 
                         float buffer_smooth_sigma,
                         int nguesses,
                         float min_distance) {
        this.frequency = frequency;
        this.frequency_sigma = frequency_sigma;
        this.nguesses = nguesses;
        this.min_distance = min_distance;
        this.buffer_smooth_sigma = buffer_smooth_sigma;

        this.buffer = new float[H][W];
        // fill with 0
        this.last_reset = 0
        this.last_event_timestamp = 0
    }

    void ProcessInterval(Interval interval) {
        // Rememebr the last time we reset the buffer
        if this.last_reset == 0:
            this.last_reset = interval.timestamp;

        // Compute how much this event should contribute for this frequency
        sigma = this.frequency_sigma
        diff = (1.0/interval.delta) - this.frequency
        weight = 1/(sigma*sqrt(2*PI)*exp(-1/2*pow(diff/sigma),2));

        // add this contribution to the buffer
        this.buffer[interval.coordinates] += weight;
        this.last_event_timestamp = interval.timestamp
    }  

    bool is_expired() {
        period = 1.0/this.frequency;
        delta = this.last_event_timestamp - this.last_reset ;
        expired = delta > period;
        return expired;
    }

    Guess[] get_guesses() {
        buffer_smooth = smooth(this.buffer, this.buffer_smooth_sigma);
        maxima = find_local_maxima(this.buffer, this.nguesses, this.min_distance);

        // For each local maxima, check that the buffer value is larger than zero
        vector<Guess> guesses;
        for(coordinates in maxima):
            if (this.buffer[coordinates] == 0)
                continue;
            timestamp  = self.last_event_timestamp;
            score = this.buffer[coordinates]
            guess = Guess(timestamp, coordinates, score)
            guesses.add(guess)

        // Erase the buffer, remember when we did it
        this.buffer.erase();
        this.last_reset = self.last_event_timestamp;

        return guesses;
    }


Coordinates[] find_local_maxima(float[][] buffer, int nguesses, float min_distance) {
    // min_distance: minimum distance between the local maxima

}

float[][]  smooth(float[][]  buffer,  float sigma) {

}



