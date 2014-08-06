import java.util.Random;
import weka.core.Instances;
import java.io.BufferedReader;
import java.io.FileReader;
import weka.core.converters.ConverterUtils.DataSource;
import weka.classifiers.trees.*;
import weka.classifiers.functions.*;
import weka.classifiers.meta.*;
import weka.classifiers.lazy.*;
import weka.classifiers.*;//Throw in the kitchen sink
import weka.classifiers.*;//Throw in the kitchen sink
public class ML{
	public static void main(String args[])throws Exception {
    	DataSource source;
    	Instances train,test;
    	source = new DataSource("Norm_training.csv.arff");
	    train = source.getDataSet();
		String options="-S 0";
		LinearRegression reg = new LinearRegression();         // new instance of tree
		reg.setOptions(weka.core.Utils.splitOptions(options));     // set the options
		//System.out.println(evalMany(reg,train,"LinearRegression"));
		IBk knn=new IBk();
//		options="weka.classifiers.lazy.IBk -K 3 -W 0 -A \"weka.core.neighboursearch.LinearNNSearch -A \\"weka.core.EuclideanDistance -R first-last\"\"";
    	String[] opt={"-K","7","-W","0","-A","weka.core.neighboursearch.LinearNNSearch -A \"weka.core.EuclideanDistance -R first-last\""};
		knn.setOptions(opt);
		System.out.println(evalMany(knn,train,"KNN-3 Regression"));
	}
	public static double evalMany(Classifier c, Instances in, String r) throws Exception{
		double sum=0;
		for (int i=4; i<64*4; i+=4){
			int toSave=i+1;
			Instances clone=new Instances (in);
			for (int j=64*4; j>toSave; j--){
				clone.deleteAttributeAt(clone.numAttributes()-1);
			}
			for(int j=toSave-1; j>4; j--){
				clone.deleteAttributeAt(clone.numAttributes()-2);
			} 
			toSave=i+2;
			sum+=evalSingle(c,clone,r+" X"+(i/4));
			clone=new Instances (in);
			for (int j=64*4; j>toSave; j--){
				clone.deleteAttributeAt(clone.numAttributes()-1);
			}
			for(int j=toSave-1; j>4; j--){
				clone.deleteAttributeAt(clone.numAttributes()-2);
			} 
			sum+=evalSingle(c,clone,r+" Y"+(i/4));
		}
		return sum;	
	}
	public static double evalSingle(Classifier c, Instances i, String r)throws Exception{
		i.setClassIndex(i.numAttributes()-1);
		Evaluation eval = new Evaluation(i);
		eval.crossValidateModel(c, i, 2, new Random(1));
		System.out.println(i.toSummaryString());
		System.out.println(eval.toSummaryString("\nResults "+r+"\n======\n", false));
		return eval.rootMeanSquaredError();
	}
}
