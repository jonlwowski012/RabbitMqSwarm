
# coding: utf-8

# In[51]:


from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
import numpy as np
import random
import matplotlib.pyplot as plt


# In[52]:


spark = SparkSession.builder.appName("KMeansExample").getOrCreate()


# In[53]:


poses = []
for i in range(100):
    poses.append((random.randint(-10,10),random.randint(-10,10)))
poses = np.array(poses)
dff = map(lambda x: (0,(Vectors.dense(x[0:2]))), poses)
mydf = spark.createDataFrame(dff,schema=["None","features"])
mydf.show(5)


# In[54]:


# Trains a k-means model.
kmeans = KMeans().setK(2).setSeed(1)
model = kmeans.fit(mydf)


# In[69]:


# Make predictions
predictions = model.transform(mydf)
#print(predictions.toPandas())
plt.figure(); 
pred = predictions.toPandas()
for index,row in pred.iterrows():
    if row['prediction'] == 0:
        plt.scatter(row['features'][0],row['features'][1], c='r')
    else:
        plt.scatter(row['features'][0],row['features'][1], c='g')


# In[38]:


# Evaluate clustering by computing Silhouette score
evaluator = ClusteringEvaluator()
silhouette = evaluator.evaluate(predictions)
print("Silhouette with squared euclidean distance = " + str(silhouette))


# In[39]:


# Shows the result.
centers = model.clusterCenters()
print("Cluster Centers: ")
for center in centers:
    print(center)


# In[40]:


spark.stop()

