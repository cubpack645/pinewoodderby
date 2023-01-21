bin/pack is the single entry point, you call it with different command arguments, and it carries out those commands.

The first command is to prepare a blank database 

	pack --pristine db rounds
		this copies pristine.sqlite from the resources database to the live location (live.sqlite)
		the rounds command creates the necessary Classes table config in the database, specifying each round
	
The next step is to create the prelims round.  This includes loading racer records from a roster csv file

	pack prelims --roster=resources/roster2023.csv

	The Roster CSV file should look like this:

	Car #,First Name,Last Name,Car Name,Den
	600,Cole,Carlson,Black Sabath,Webelo 2
	605,Henry,LeVeque,You-look-sus,Webelo 2
	608,Matthew,Njaa,Green light means go,Webelo 2
	609,Eli,Schwartz,Metallic,Webelo 2
	610,Dilan,Shah,Hydro,Webelo 2
	611,Andres,Strittmatter,Smashy Road Rocket Launcher,Webelo 2
	500,Luke,Van Veen,Galatic Gold,Webelo 1
	501,Jack,Crowley,Mr. Quackers Car,Webelo 1
	502,Kiran,Shu,The Pencil,Webelo 1
	...

	and the Dens should be:

	Lion
	Tiger
	Wolf
	Bear
	Webelo 1
	Webelo 2
	Siblings
	Parents

Now you need to print off the schedule sheets for the prelims from the GP software

todo: add steps for printing off prelim from GP

Note that we can't yet generate schedules for the Den races, because we will seed those in time-descending order, ie. so that the fastest cars in a den race together (relevant only when there are > 8 cars in a den, such that more than one race is needed).

Once the prelim rounds have been completed we will have recorded the times we need to populate the den, pack slowest final and pack fastest semi-finals

	pack dens slowest semis

And now you can print off the schedule sheets for these three

Once the semi final racing has been completed, you need to create the schedule for the final.  Note that we take the 2 fastest from prelims direct into the final
plus the fastest 3 from each of the 2 semi finals

	pack final

You can now print off the schedule for the final (and finally, run the race in GP)

Note on Dry-Run testing
=======================

You can create mock results for certain rounds to allow for end-to-end testing of all this.

For example:

	pack --pristine db rounds prelims mockprelims dens mockdens slowest semis mocksemis final

	will do everything up to (but excluding) the Pack Slowest and Pack Final timings

