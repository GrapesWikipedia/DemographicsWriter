# Using This Puppy
So, you're here, and you probably wanna use the code to generate some demographic formatting. To run it, all you've gotta do is download this github folder (if you're on the github website, then press that green button labeled "Code" on the upper right bit of the screen, press Download ZIP (I have no idea what it looks like on Windows...). Then unzip the file.

Then you use your preferred Python running environment and run `WriteDemographicsSectionRelease.py` which, if you're in the command line would be done with the command (assuming that you've `cd`-ed into the folder) `python3 WriteDemographicsSectionRelease.py`. If you don't have Python, download it from [their website](https://www.python.org/downloads/)!

Then just follow the instructions given on the screen, and you should be golden. If you don't have an API Key from the Census you'll have to get it, but that's already in the instructions.

## More Advanced Instructions
If you want to test out your own formatting options, use `h = CensusWriter("YOUR API KEY", test_mode=True)`, and make a new function for formatting, and run it on whatever location you want.

# Guide to the puppy itself
All of these words hopefully could possibly helpful if you wanna change things. If you don't wanna change things and just want to run it, none of this section will be important.
## Census Getter
This is what I use to get data from the ACS. If you want to get another piece of data, you can look at a variable list such as from [here](https://www.census.gov/data/developers/data-sets/acs-5year.html) under variable changes, and find the variable you want to add (making sure to use the 2022 version if applicable). Then you add it to the init_params function, and if the letters before the first underscore is not in self.table_names, you'll have to add the table name too. Those oughta be the only changes you've gotta make.

This class both does the necessary API queries, and also, given a parameter name, returns a correspodning citation.

## Census Writer
This actually spits out the string corresponding to a demographics page, given a row of the Place table from ansi. I'm pretty sure the elements are properly explained. If you want to add another sentence, then write elements.extend where you want to add it. If you're going to implement a new type, then you'll have to define it outside the class with the other ones, and also add an elif statement to read_elements_acs.

# Other stuff I'm too lazy to organize
* If something's going wrong or you want any help running jazz go to [my Talk page](https://en.wikipedia.org/wiki/User_talk:GrapesRock) and holler a question there.
* Feel free to make PRs and whatever and I'll take a look at 'em (A comment on my talk page if/when you do that would be great cause I feel like there's some vibe that off-wiki conversations are bad? Idk if that's true)! You can also make vaguer suggestions, or simply feedback on my Talk Page which I'll try to implement if I think they're groovy :-).
* I have a variety of questions sprinkled throughout (prefixed with QUESTION:) which aren't particularly rhetorical. If you have thoughts, throw 'em on my Talk Page!
# License
I chucked in the GPL3 license because it felt like a good idea to have some sorta license? It's pretty permissive, though viral, so hopefully it's good!