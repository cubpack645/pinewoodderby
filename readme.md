This repository contains the code that supports the running of the Cub Scouts Pack 645 Pinewood Derby.

## Background 

The event is run using 'Grand Prix Race Manager' from [grand-prix-software central.com](https://grandprix-software-central.com/). (We are using [version 18.0](https://grandprix-software-central.com/index.php/downloads/gprm)).  This runs on Windows or MacOS.  Talk to your Pack 645 pinewood derby person about obtaining a licence key.

The software in this repository consists of a script that interacts with the Grand Prix database in various ways, for example:
* populating a roster of racers
* creating race schedules that fit with the way that Pack 645 structures its derby.
* custom reporting that helps in organizing cars on race day.

A [docker image](https://hub.docker.com/repository/docker/cubpack645/pinewoodderby/general) is the recommended way to run this script.  So you should not really need the code in this 
repo unless you are looking to make modifications to it.

You will however need the related repo: [cubpack645/pinewoodderby-data](https://github.com/cubpack645/pinewoodderby-data.git) which contains data needed for running the event, and also serves as the historical record for race results.

## Getting Started

### Step 1: Grand Prix Race Manager

Download & install the Race Manager software from the link above, and enter the licence key you have been provided separately.

### Step 2: Checkout the data repository

Choosing some suitable location (e.g. your home directory, or a cubscouts folder, etc)

```shell
git clone https://github.com/cubpack645/pinewoodderby-data.git
```

### Step 3: Run the docker image

```shell
docker run -it --rm --name derby -e DJANGO_SETTINGS_MODULE=derby.settings.docker -v path/to/pinewoodderby-data:/data cubpack645/pinewoodderby bash
```

(replacing path/to/pinewoodderby-data with the location you chose).

You should be within the /app folder, where a **pack** entry point script lives.  /data should contain the mounted pinewoodderby-data folder.

### Step 4: Test that everything is working

We will create a blank database, ready for running a new event

```shell
./bin/pack db --db=resources/pristine.sqlite
```

Now run Grand Prix Race Manager, and open the database file live.sqlite located within your pinewoodderby-data folder.  If that opens ok, then you are
all set and we can move on to how to run an actual event.

## Running an Event

**pack** is the single entry point, you call it with different command arguments, and it carries out those commands.

### Step 1: Before the race
The first command is to prepare a blank database, and populate some basic data about the rounds that we will run

```shell
./bin/pack db rounds --db=resources/pristine.sqlite
```
	
The next step is to create the prelims round.  This includes loading racer records from a roster csv file that you specify with the --roster param.  
The path you provide is relative to the pinewoodderby-data folder.

```shell
./bin/pack prelims --roster=2023/roster2023.csv
```
The Roster CSV file should look like this:

```csv
	Car #,First Name,Last Name,Car Name,Den
	100,John,Smith,Blue Thunder,Lion
	...
```

and the Den names should be:

	Lion
	Tiger
	Wolf
	Bear
	Webelo 1
	Webelo 2
	Siblings
	Parents

Now you need to print off the schedule sheets for the prelims from the GP software

### Step 2: Race day - Prelims

Ok, its race day, you get the track & the timing unit set up & configured.  Run through the Prelims using Grand Prix.  Once the last prelims race is configured, we can now create the schedules for the Dens Finals, the Pack Slowest final, and the Pack Fastest Semi Finals.

```shell
./bin/pack dens slowest semis finaltop2 densched
```

Now you can print off the schedule sheets for the next 3 rounds (Den Finals, Pack Slowest, Pack Semi Finals).  The purpose of the **finaltop2** command is to push the fastest 2 racers from Prelims directly to the Fastest Final.  The next 16 fastest racers have to battle it out in the Semi Finals for the right to advance.  The last command **densched** generates a custom Den Finals schedule report (**den_finals_custom.pdf** in the data folder) that tells the Race Set up crew which of the finishing Den cars to sequester for the next-to-run Slowest, Semi-Final and Final rounds.  If that doesn't make sense, it will when you see it.

### Step 3: Den Finals, Slowest, Fastest Semi Finals

Run these rounds of races in Grand Prix.

### Step 4: Pack Fastest Final

With the semi finals complete, we can now create the schedule for the Fastest Final ... comprising the fastest 2 cars from Prelims plus the 3 fastest from each of the 2 semi finals.

```shell
./bin/pack final
```
You can now print off the schedule for the final (and finally, run the race in GP)

### Note on Dry-Run testing

You can create mock results for certain rounds to allow for end-to-end testing of all this ahead of time.

For example, having created prelim schedules you can fake times for those races with this command:

```shell
./bin/pack mockprelims --dryrun
```

The --dryrun parameter is required as a safety measure, to make sure you are running the mock command intentionally (as it will overwrite any existing prelims results).

There are similar mock commands for the other rounds: mockdens mockslowest mocksemis mockfinal

Good luck!
