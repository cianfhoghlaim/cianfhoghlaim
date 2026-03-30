/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;

/**
 *
 * @author fosterjen
 */
public class IrishDependencyTreebank {
<<<<<<< Updated upstream
    static ArrayList<Sentence> sentences = new ArrayList();
=======
    static ArrayList sentences = new ArrayList();
>>>>>>> Stashed changes
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) 
    {   
        try
        {
            int lineCount = 0;
            BufferedReader b = new BufferedReader(new FileReader(new File(args[0])));
            String line = b.readLine();
<<<<<<< Updated upstream
            ArrayList<String> lines;
            while (line != null)
            {
                //System.out.println(line);
                lines = new ArrayList<String>();
                while (line != null && line.length() >1)
                {
                    lines.add(line);
                    line = b.readLine();
                    //System.out.println(line);
                }
                sentences.add(new Sentence(lines));
                line = b.readLine();
            }      
            b.close();
            //processPP();
            //processCopula();
            //processProPreps();
	    processPPXComp();
            printSentences();
=======
            
            while (line != null)
            {
                sentences.add(line);
                line = b.readLine();         
            }      
            b.close();
             //processPP(sentences);
             processCopula(sentences);
             printSentences(sentences);
>>>>>>> Stashed changes
        }
        catch (IOException io)
        {
            System.out.println(io.getMessage());
        }
       
    }
    
<<<<<<< Updated upstream
    public static void processPP() 
=======
    public static void processPP(ArrayList sentences) 
>>>>>>> Stashed changes
    {
        Sentence sentence;
                  
        for (int i=0; i < sentences.size(); i++)
        {
            sentence = (Sentence) sentences.get(i); 
            
            //does the sentence contain a case relation?
            //if it does, find the nmod that it is related to
            ArrayList<Word> caseWords = sentence.findWords("case");
            for (int j=0; j < caseWords.size(); j++)
            {
                Word caseWord = caseWords.get(j);
            
                ArrayList<Word> nmodWords = sentence.findDependents(caseWord);
                if (nmodWords.size() == 0)
                {
                    //no nmod, mark it
                    caseWord.setToken("***"+ caseWord.getToken()+"***");
                }
                else
                {
                    for (int k=0; k < nmodWords.size(); k++)
                    {
                        Word nmodWord = nmodWords.get(k);
                    
                       
                        if (nmodWord.getHead() == caseWord.getId())
                        {
                            nmodWord.setHead(caseWord.getHead());
                            caseWord.setHead(nmodWord.getId());
                        }
                    }       
                }
            }
        }        
    }


    public static void processAspectualPhrases()
    {
	Sentence sentence;

	for (int i=0; i < sentences.size(); i++)
	    {
		sentence = (Sentence) sentences.get(i);
		ArrayList<Word> xcompWords = sentence.findWords("xcomp");
		for (int j=0; j < xcompWords.size(); j++)
		    {
			Word xcompWord = xcompWords.get(j);
			if (xcompWord.getLemma().equals("ag"))
			    {
				ArrayList<Word> dependentWords = sentence.findDependents(xcompWord);
				if (dependentWords.size() == 0)
				    {

					//something strange going on - mark it
					xcompWord.setToken("@@@"+ xcompWord.getToken()+"@@@");
				    }
			   
		    
		else if (dependentWords.size() == 1)
		    {

			Word dependentWord = dependentWords.get(0);
			if (dependentWord.getRelation().equals("dobj"))
			    {
				dependentWord.setRelation(xcompWord.getRelation());
				dependentWord.setHead(xcompWord.getHead());
				xcompWord.setRelation("case");
				xcompWord.setHead(dependentWord.getId());
			    }
			else
			    {
				//something strange going on - mark it
				xcompWord.setToken("@@@"+ xcompWord.getToken()+"@@@");

			    }


		    }
		else {

		    for (int k=0; k < dependentWords.size(); k++)
			{
			    Word dependentWord = dependentWords.get(k);
			    dependentWord.setHead(xcompWord.getHead());
			    if (dependentWord.getRelation().equals("dobj"))
				{
				    xcompWord.setHead(dependentWord.getId());
				    dependentWord.setRelation(xcompWord.getRelation());
				}
			}
		    xcompWord.setRelation("case");
		}
	    }

	    }
	    }
    }

    
    public static void processPPXComp()
    {
	Sentence sentence;

	for (int i=0; i < sentences.size(); i++)
	    {
		sentence = (Sentence) sentences.get(i);

		//does the sentence contain a case relation?
		//if it does, find the nmod that it is related to
		ArrayList<Word> xcompWords = sentence.findWords("xcomp:pred");
		for (int j=0; j < xcompWords.size(); j++)
		    {
			Word xcompWord = xcompWords.get(j);
			if (xcompWord.getPosCoarse().equals("ADP"))
			    {

				ArrayList<Word> dependentWords = sentence.findDependents(xcompWord);
				if (dependentWords.size() == 0)
				    {
					//no nmod
					if (isProPrep(xcompWord.getToken(),xcompWord.getLemma()))
					    {
						xcompWord.setToken("%%%"+ xcompWord.getToken()+"%%%");
					    }
					    else
					    {
						//something strange going on - mark it
						xcompWord.setToken("$$$"+ xcompWord.getToken()+"$$$");
					    }
				    }
				else if (dependentWords.size() == 1)
				    {
					Word dependentWord = dependentWords.get(0);
					dependentWord.setRelation(xcompWord.getRelation());
					dependentWord.setHead(xcompWord.getHead());
					xcompWord.setRelation("case");
					xcompWord.setHead(dependentWord.getId());
				 
					
				    }
				else {
				    
					for (int k=0; k < dependentWords.size(); k++)
					    {
						Word dependentWord = dependentWords.get(k);
						dependentWord.setHead(xcompWord.getHead());
						if (dependentWord.getRelation().equals("nmod") || dependentWord.getRelation().startsWith("xcomp"))
						    {
							xcompWord.setHead(dependentWord.getId());
							dependentWord.setRelation(xcompWord.getRelation());
						    }
						
						
					    }
					xcompWord.setRelation("case");
				    }
			    }
			   
		    }	
	    }
    }
            
    public static void processCopula() 
    {
        Sentence sentence;
        for (int i=0; i < sentences.size(); i++)
        {
            sentence = (Sentence) sentences.get(i);
            //does the sentence contain a copula?
            ArrayList<Word> copWords = sentence.findWordsByLemma("is");
            for (int j=0; j < copWords.size(); j++)
            {
                Word copWord = (Word) copWords.get(j);
                //check that the word is not a mark:prt
                if (!copWord.getRelation().equals("mark:prt"))
                {
                    //look for the xcomp
                    ArrayList<Word> xcompWords = sentence.findWords("xcomp:pred");
                    xcompWords.addAll(sentence.findWords("xcomp"));
                    if (xcompWords.size() == 0)
                    {
                        //no xcomp, something strange going on
                        copWord.setToken("+++"+copWord.getToken()+"+++");
                    }
                    for (int k=0; k < xcompWords.size(); k++)
                    {
                        Word xcompWord = xcompWords.get(k);
                        if (xcompWord.getHead() == copWord.getId())
                        {
                            xcompWord.setHead(copWord.getHead());
                            xcompWord.setRelation(copWord.getRelation());
                            copWord.setHead(xcompWord.getId());
                            copWord.setRelation("cop");
                        }
                    }
                    //look for other dependents of the copula
                    ArrayList<Word> otherDeps = sentence.findDependents(copWord);
                    for (int x=0; x < otherDeps.size(); x++)
                    {
                        Word dep = otherDeps.get(x);
                        dep.setHead(copWord.getHead());
                    }
                }
                
            }
        }  
    }
    
    public static void processProPreps()
    {
        for (int i=0; i < sentences.size(); i++)
        {
            Sentence sentence = sentences.get(i);
            ArrayList<Word> caseWords = sentence.findWords("case");
            for (int j=0; j < caseWords.size(); j++)
            { 
                Word caseWord = caseWords.get(j);
                if (caseWord != null && caseWord.getToken().startsWith("***"))
                {
<<<<<<< Updated upstream
                    if (isProPrep(caseWord.getToken().substring(3,caseWord.getToken().length()-3),caseWord.getLemma()))
                    {
                         caseWord.setToken(caseWord.getToken().substring(3,caseWord.getToken().length()-3));
                         caseWord.setRelation("nmod:prep");
                    }
                }
            }
        }
    }
    
    
    public static void printSentences()
    {
         for (int i=0; i < sentences.size(); i++)
        {
            System.out.println(sentences.get(i));
        }      
    }

    private static boolean isProPrep(String token, String lemma) 
    {
        //String [] proPrepList = {"agam","agat","aige","aici","againn","agaibh","acu","liom","leat","leis","leí","linn","libh","leo"
                 //,"orm","ort","air","uirthi","orainn","oraibh","orthu","dom","duit","dó","dúinn","daoibh","dóibh","uaim","uait",
        //"uaidh","domsa"};
        String [] prepList = {"do","ag","ar","le","de","faoi","ó","chuig","roimh","i","trí","as","thar"};
        for (int i=0; i < prepList.length;i++)
        {
            if (prepList[i].equalsIgnoreCase(lemma) && !lemma.equalsIgnoreCase(token) && !token.equalsIgnoreCase("lena") && !token.equalsIgnoreCase("lenar") &&
		!token.equalsIgnoreCase("don") && !token.equalsIgnoreCase("den") && !token.equalsIgnoreCase("d'"))
            {
                return true;
            }
        }
        return false; //To change body of generated methods, choose Tools | Templates.
=======
                    sentences.set(prepLine,"***"+line+"***");
                }
            }
        }
       
    }
    
    public static void processCopula(ArrayList sentences) 
    {
        int lineCount = 0, copLine = 0, predLine = 0;
        String line;
       
        for (int i=0; i < sentences.size(); i++)
        {
            line = (String) sentences.get(i); 
            boolean isNotAPred = false;
            boolean isNotASubj = false;
            boolean finishedSentence = false;
            boolean finishedFile = false;
            //System.out.println("LINE" + line);
            lineCount++;
            String nextLine;
            String [] tokens = line.split("\t");    
            if (tokens.length > 1 && tokens[2].equals("is") &&!tokens[7].equals("mark:prt"))
            {
                String copId = tokens[0];
                String copHeadId = tokens[6];
                copLine = i;
                lineCount = i;
                
                String [] predTokens = null;
                String predHead = null;
                String predId = null;
                String [] subjTokens = null;
                String subjHead = null;
                
                do
                {
                    lineCount++;
                    isNotAPred = false;
                    nextLine = (String) sentences.get(lineCount);
                    //System.out.println("NEXTLINE " + nextLine);
                        
                    if (nextLine == null)
                    {
                        finishedFile = true;
                    }
                    else if (nextLine.length() <= 1)
                    {
                        finishedSentence = true;     
                    }
                    else 
                    {
                        predTokens = nextLine.split("\t");
                        predId = predTokens[0];
                        predHead = predTokens[6];
                        if (!predTokens[7].startsWith("xcomp") || !predHead.equals(copId))
                        {
                            //System.out.println("not a pred");
                            isNotAPred = true; 
                        }    
                    }             
                }while (isNotAPred && !finishedSentence && !finishedFile);
                   
                if (!finishedSentence && !finishedFile)
                {
                    //the new head of the pred is the head of the cop
                    predTokens[6] = copHeadId;
                    //the relation associated with the cop is now associated with the pred
                    predTokens[7] = tokens[7];
                    //the new head of the cop is the pred
                    tokens[6] = predId;
                    //the cop's relation to the pred is "cop"
                    tokens[7] = "cop";
                    predLine = lineCount;
                    //now find the subj of the predicate and anything else that used to depend on the copula verb
                    String anotherLine = null;
                    do
                    {
                        lineCount++;
                        anotherLine = (String) sentences.get(lineCount);
                        //System.out.println("NEXTLINE " + anotherLine);
                        
                        if (anotherLine == null)
                        {
                            finishedFile = true;
                        }
                        else if (anotherLine.length() <= 1)
                        {
                            finishedSentence = true;     
                        }
                        else 
                        {
                            subjTokens = anotherLine.split("\t");
                            subjHead = subjTokens[6];
                            if (subjHead.equals(copId))
                            {
                                subjTokens[6] = predId;
                                anotherLine = "";
                                for (int x=0; x < subjTokens.length-1; x++)
                                {
                                    anotherLine += subjTokens[x] + "\t";
                                }
                                anotherLine += subjTokens[subjTokens.length-1];
                                sentences.set(lineCount,anotherLine);
                            }    
                        }             
                    }while (!finishedSentence && !finishedFile);
                    
                    line = ""; nextLine = "";
                    for (int k=0; k < tokens.length-1; k++)
                    {
                        line += tokens[k] + "\t";
                    }
                    line += tokens[tokens.length-1];
                    for (int j=0; j < predTokens.length-1; j++)
                    {
                        nextLine += predTokens[j] + "\t";
                    }
                    nextLine += predTokens[predTokens.length-1];
                    sentences.set(copLine,line);
                    sentences.set(predLine,nextLine);
                }
                else if (finishedSentence || finishedFile)
                {
                    sentences.set(copLine,"+++"+line+"+++");
                }
            }
        }
       
    }
    public static void printSentences(ArrayList sentences)
    {
         for (int i=0; i < sentences.size(); i++)
        {
            System.out.println(sentences.get(i));
        }      
>>>>>>> Stashed changes
    }

    
}
