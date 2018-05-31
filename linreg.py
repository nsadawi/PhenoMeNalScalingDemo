# export PYTHONPATH=./ 
# luigi --module linreg LinRegAllDatasets --scheduler-host luigi-service.default --workers 100

import luigi
from luigi.contrib.kubernetes import KubernetesJobTask
import glob
  
class LinRegTask(KubernetesJobTask):
    
    datasetFile = luigi.Parameter()
    name = "lin-reg"
    max_retrials = 1
    
    @property
    def spec_schema(self): 
        return {
            "containers": [{
                "name": self.name,
                "image": "nsadawi/lin-reg",
                "args": [
                    self.datasetFile,
                ],
                "resources": {
                  "requests": {
                    "memory": "1G",
                    "cpu": "1"
                  },
                  "limits": {
                    "memory": "1G",
                    "cpu": "1"
                  }
                },
                "volumeMounts": [{
                    "mountPath": "/work", # inside the container
                    "name": "shared-volume",
                    "subPath": "jupyter/LinReg" # on host .. i.e. where we run this script
                 }]
             }],
             "volumes": [{
                 "name": "shared-volume",
                 "persistentVolumeClaim": {
                     "claimName": "galaxy-pvc"
                 }
             }]
        }
    
    def output(self):
        filename = self.datasetFile + ".out"
        return luigi.LocalTarget(filename)

class LinRegAllDatasets(luigi.WrapperTask):
    def requires(self):
        inputFiles = glob.glob("randomised-datasets/*.csv")
        for inputFile in inputFiles:
            yield LinRegTask(datasetFile=inputFile)