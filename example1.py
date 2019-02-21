import rx
from rx.concurrency import CurrentThreadScheduler

my_scheduler = CurrentThreadScheduler()

# create an shared observable emitting a single element "3"
shared_obs = rx.Observable.just(3, scheduler=my_scheduler).share()

# take the first element of the shared observable
left_obs = shared_obs.first()
right_obs = shared_obs.first()

# zip the two single element observables
out_obs = rx.Observable.zip([left_obs, right_obs])

out_obs.subscribe(print)