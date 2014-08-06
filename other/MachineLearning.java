import weka.core.Instances;
import java.io.BufferedReader;
import java.io.FileReader;
import weka.core.converters.ConverterUtils.DataSource;
import weka.classifiers.trees.*;
import weka.classifiers.functions.*;
import weka.classifiers.meta.*;
import weka.classifiers.lazy.*;
import weka.classifiers.*;//Throw in the kitchen sink
public class MachineLearning{
  public static String eval(Object model, Instances train, Instances test) throws Exception{
    Classifier m=(Classifier)model;
    Evaluation eval = new Evaluation(train);
    eval.evaluateModel(m, train);
    double trainPct=eval.pctCorrect();
    eval.evaluateModel(m, test);
    double testPct=eval.pctCorrect();
    return trainPct+","+testPct;
  }
  public static void main(String args[])throws Exception{
    DataSource source;
    Instances train,test;

    source = new DataSource("AccidentTest.arff");
    train = source.getDataSet();
/*    source = new DataSource("Accident5.arff");
    train = source.getDataSet();
    run("Accident,5",train, test);

    source = new DataSource("Accident50.arff");
    train = source.getDataSet();
    run("Accident,50",train, test);

    source = new DataSource("Accident500.arff");
    train = source.getDataSet();
    run("Accident,500",train, test);

    source = new DataSource("Accidents5000.arff");
    train = source.getDataSet();
    run("Accident,5000",train, test);

    source = new DataSource("Accidents50000.arff");
    train = source.getDataSet();
    run("Accident,50000",train, test);

    source = new DataSource("Accidents120000.arff");
    train = source.getDataSet();
    run("Accident,120000",train, test);

    source = new DataSource("ChildInfoTest.arff");
    test = source.getDataSet();
    source = new DataSource("ChildInfo10.arff");
    train = source.getDataSet();
    run("Child,10",train, test);

    source = new DataSource("ChildInfo100.arff");
    train = source.getDataSet();
    run("Child,100",train, test);

    source = new DataSource("ChildInfo1000.arff");
    train = source.getDataSet();
    run("Child,1000",train, test);


    source = new DataSource("ChildInfo7000.arff");
    train = source.getDataSet();
    run("Child,7000",train, test);
*/

    //Evaluate
    /*for(data files)
        for(algorithms)
    */
  }
  //The core method: Run every data set with every machine learning method.
  public static void run(String source, Instances train, Instances test)throws Exception{
    long startTime;
    long endTime;
    String[] opt={"-K","1","-W","0","-A","weka.core.neighboursearch.LinearNNSearch -A \"weka.core.EuclideanDistance -R first-last\""};
   String options;
  /*  train.setClassIndex(train.numAttributes() - 1);
    test.setClassIndex(test.numAttributes() - 1);
    //K Nearest Neighbors
      //Different forms of K
    IBk knn = new IBk();
    knn.setOptions(opt);
    startTime=System.nanoTime();
    knn.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",KNN,1,"+eval(knn, train,test)+","+(endTime-startTime));
    knn = new IBk();
    String[] opt2={"-K","1","-W","0","-A","weka.core.neighboursearch.LinearNNSearch -A \"weka.core.EuclideanDistance -R first-last\""};
    knn.setOptions(opt2);
    startTime=System.nanoTime();
    knn.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",KNN,10,"+eval(knn, train,test)+","+(endTime-startTime));
    knn = new IBk();
    String[] opt3={"-K","1","-W","0","-A","weka.core.neighboursearch.LinearNNSearch -A \"weka.core.EuclideanDistance -R first-last\""};
    knn.setOptions(opt3);
    startTime=System.nanoTime();
    knn.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",KNN,100,"+eval(knn, train,test)+","+(endTime-startTime));
    //SVM
    SMO svm = new SMO();
    options="weka.classifiers.functions.SMO -C 1.0 -L 0.0010 -P 1.0E-12 -N 0 -V -1 -W 1 -K \"weka.classifiers.functions.supportVector.PolyKernel -C 250007 -E 1.0\"";
    svm.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    svm.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",SVM,"+options+","+eval(svm, train,test)+","+(endTime-startTime));
    
    svm = new SMO();
    options="weka.classifiers.functions.SMO -C 1.0 -L 0.0010 -P 1.0E-12 -N 0 -V -1 -W 1 -K \"weka.classifiers.functions.supportVector.RBFKernel -C 250007 -G 0.01\"";
    svm.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    svm.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",SVM,"+options+","+eval(svm, train,test)+","+(endTime-startTime));
    
      //Two Kernel functions
    //Decision trees
    J48 tree = new J48();
    options="-C 0.05 -M 2";
    tree.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    tree.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",J48,"+options+","+eval(tree, train,test)+","+(endTime-startTime));
      //Different forms of pruning
    tree = new J48();
    options="-C .1 -M 2";
    tree.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    tree.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",J48,"+options+","+eval(tree, train,test)+","+(endTime-startTime));
    tree = new J48();
    options="-C .25 -M 2";
    tree.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    tree.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",J48,"+options+","+eval(tree, train,test)+","+(endTime-startTime));
    tree = new J48();
    options="-C .5 -M 2";
    tree.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    tree.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",J48,"+options+","+eval(tree, train,test)+","+(endTime-startTime));
    tree = new J48();
    options="-C .75 -M 2";
    tree.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    tree.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",J48,"+options+","+eval(tree, train,test)+","+(endTime-startTime));
*/
    //Neural networks
    MultilayerPerceptron net=new MultilayerPerceptron();
    options="-L 0.3 -M 0.2 -N 500 -V 0 -S 0 -E 20 -H 0";
    net.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    net.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",MultiLayerPerceptron,"+options+","+eval(net, train,test)+","+(endTime-startTime));
    net=new MultilayerPerceptron();
    options="-L 0.3 -M 0.2 -N 500 -V 10 -S 0 -E 20 -H 0";
    net.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    net.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",MultiLayerPerceptron,"+options+","+eval(net, train,test)+","+(endTime-startTime));
    net=new MultilayerPerceptron();
    options="-L 0.3 -M 0.2 -N 500 -V 0 -S 0 -E 20 -H 1";
    net.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    net.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",MultiLayerPerceptron,"+options+","+eval(net, train,test)+","+(endTime-startTime));
    net=new MultilayerPerceptron();
    options="-L 0.3 -M 0.2 -N 500 -V 10 -S 0 -E 20 -H 1";
    net.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    net.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",MultiLayerPerceptron,"+options+","+eval(net, train,test)+","+(endTime-startTime));
   /* 
    //Boosing
    AdaBoostM1 b=new AdaBoostM1();
    options="-P 100 -S 1 -I 10 -W weka.classifiers.trees.J48 -- -C 0.01 -M 2";
    b.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    b.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",Adaboost,"+options+","+eval(b, train,test)+","+(endTime-startTime));
    //Different Tree Pruning
     b=new AdaBoostM1();
    options="-P 100 -S 1 -I 10 -W weka.classifiers.trees.J48 -- -C 0.15 -M 2";
    b.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    b.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",Adaboost,"+options+","+eval(b, train,test)+","+(endTime-startTime));
     b=new AdaBoostM1();
    options="-P 100 -S 1 -I 10 -W weka.classifiers.trees.J48 -- -C 0.5 -M 2";
    b.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    b.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",Adaboost,"+options+","+eval(b, train,test)+","+(endTime-startTime));
     b=new AdaBoostM1();
    options="-P 100 -S 1 -I 10 -W weka.classifiers.trees.J48 -- -C 0.7 -M 2";
    b.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    b.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",Adaboost,"+options+","+eval(b, train,test)+","+(endTime-startTime));
     b=new AdaBoostM1();
    options="-P 100 -S 1 -I 100 -W weka.classifiers.trees.J48 -- -C 0.15 -M 2";
    b.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    b.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",Adaboost,"+options+","+eval(b, train,test)+","+(endTime-startTime));
     b=new AdaBoostM1();
    options="-P 100 -S 1 -I 500 -W weka.classifiers.trees.J48 -- -C 0.15 -M 2";
    b.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    b.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",Adaboost,"+options+","+eval(b, train,test)+","+(endTime-startTime));
     b=new AdaBoostM1();
    options="-P 100 -S 1 -I 1000 -W weka.classifiers.trees.J48 -- -C 0.15 -M 2";
    b.setOptions(weka.core.Utils.splitOptions(options));
    startTime=System.nanoTime();
    b.buildClassifier(train);
    endTime=System.nanoTime();
    System.out.println(source+",Adaboost,"+options+","+eval(b, train,test)+","+(endTime-startTime));
    
    */
  }
}
