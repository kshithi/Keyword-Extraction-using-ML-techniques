import rake
import operator

filepath = "keyword_extraction.txt"
rake_object = rake.Rake(filepath)
text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered.Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generatingsets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types of systems and systems of mixed types."
sample_file = open(“data/docs/fao_test/w2167e.txt”, ‘r’)
text = sample_file.read()
keywords = rake_object.run(text)
print (“Keywords:”, keywords)
