```python
PyRDF.use('spark')

rdf = PyRDF.RDataFrame(...)

rdf_column_1 = rdf.Define(...) # Transformation
rdf_column_2 = rdf.Define(...) # Transformation
rdf_filtered_1 = rdf_column_1.Filter(...) # Transformation
rdf_count_1 = rdf_filtered_1.Count(...) # Action
rdf_histogram_1 = rdf_column_2.Histo1D(...) # Action

rdf_histogram_1.Draw()
print(rdf_count_1.GetValue())
```
