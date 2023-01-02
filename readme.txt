bin/pack is the single entry point, you call it with different command arguments, and it carries out those commands.

The first command is to prepare a blank database 

	pack --pristine db rounds
		this copies pristine.sqlite from the resources database to the live location (live.sqlite)
		the rounds command creates the necessary Classes table config in the database, specifying each round
	
The next step is to create the prelims round.  This includes loading racer records from a roster csv file

	pack prelims --roster=resources/roster2020.csv

	Roster CSV file should look like this:

	Car #,Last Name,First Name,Group 
	102,Cruz,Enzo,Lion
	104,Meinberg,Evan,Lion
	105,Strum,Grant,Lion
	106,Bishop,Issac,Lion
	108,Shu,Kiran,Lion
	109,Van Veen,Luke,Lion
	201,Hedrick-Choi,Caden,Tiger
	202,Carlson,Cole,Tiger
	205,Schwartz,Eli,Tiger

	and the Dens should be:

	Lion
	Tiger
	Wolf
	Bear
	Webelo 1
	Webelo 2
	Siblings
	Parents

At this point you can also create the Dens schedule:

	pack dens

Now you need to print off the schedule sheets for prelims and den races from the GP software

todo: add steps for printing off prelim and den schedules from GP

Once the prelim rounds have been completed we will have recorded the times we need to populate the pack slowest final and pack fastest semi-finals

	pack slowest semis

And now you can print off the schedule sheets for these two

Once the semi final racing has been completed, you need to create the schedule for the final.  Note that we take the 2 fastest from prelims direct into the final
plus the fastest 3 from each of the 2 semi finals

	pack final

You can now print off the schedule for the final (and finally, run the race in GP)

Note on Dry-Run testing
=======================

You can create mock results for certain rounds to allow for end-to-end testing of all this.

For example:

	pack --pristine db rounds prelims dens mockprelims mockdens slowest semis mocksemis final

	will do everything up to (but excluding) the Pack Slowest and Pack Final timings

