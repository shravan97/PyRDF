```python

rdf = ROOT.ROOT.RDataFrame(...)

def mapper(rdf):
  rdf_column_1 = rdf.Define(...) # Transformation
  rdf_column_2 = rdf.Define(...) # Transformation
  rdf_filtered_1 = rdf_column_1.Filter(...) # Transformation
  rdf_count_1 = rdf_filtered_1.Count(...) # Action
  rdf_histogram_1 = rdf_column_2.Histo1D(...) # Action
  
  return rdf_count_1, rdf_histogram_1

def reducer(value1, value2):
  .....

dTree = DistTree(...)

values = dTree.ProcessAndMerge(mapper, reducer)
values[1].Draw()
```
