/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


import java.util.ArrayList;
/**
 *
 * @author fosterjen
 */
public class Sentence 
{
   ArrayList<Word> words;
   
   public Sentence(ArrayList<String> lines)
   {
       words = new ArrayList();
       for (int i=0; i < lines.size(); i++)
       {
           words.add(new Word(lines.get(i)));
       }   
   }
   
   
   public boolean containsRelation(String rel)
   {
       for (int i =0; i < words.size(); i++)
       {
           Word w = words.get(i);
           if (w.getRelation().equals(rel))
           {
               return true;
           }
       }
       return false;
   }
   
   public ArrayList<Word> findWords(String rel)
   {
       ArrayList<Word> relWords = new ArrayList<Word>();
       for (int i =0; i < words.size(); i++)
       {
           Word w = words.get(i);
           if (w.getRelation().equals(rel))
           {
               relWords.add(w);
           }
       }
       return relWords;
   }
   
   public ArrayList<Word> findWordsByLemma(String lemma)
   {
       ArrayList<Word> lemmaWords = new ArrayList<Word>();
       for (int i =0; i < words.size(); i++)
       {
           Word w = words.get(i);
           if (w.getLemma().equals(lemma))
           {
               lemmaWords.add(w);
           }
       }
       return lemmaWords;
   }
   
   public ArrayList<Word> findDependents(Word word)
   {
       ArrayList<Word> depWords = new ArrayList<Word>();
       for (int i =0; i < words.size(); i++)
       {
           Word w = words.get(i);
           if (w.getHead() == word.getId())
           {
               depWords.add(w);
           }
       }
       return depWords;
   }
   
   
   
  
  

   
   public String toString()
   {
       String sentenceStr = "";
       for (int i=0; i < words.size(); i++)
       {
           sentenceStr += words.get(i) +"\n";
       }
       return sentenceStr;
   }
   
   public void swapHead(int oldHead, int newHead)
   {
       //System.out.println("swapping heads");
       int oldHeadHead = -1;
       for (int i=0; i < words.size(); i++)
       {
           Word w = words.get(i);
            
           if (w.getId() == oldHead)
           {
               oldHeadHead = w.getHead();
               w.setHead(newHead);
               //System.out.println(w.getHead());
               words.set(i,w);
               break;
           }
       }
       for (int i=0; i < words.size(); i++)
       {
           Word w = words.get(i);
           if (w.getId() == newHead)
           {
               w.setHead(oldHeadHead);
               //System.out.println(w.getHead());
               words.set(i,w);
               break;
           }
       }
       /*for (int i=0; i < words.size(); i++)
       {
           System.out.println(words.get(i));
       }*/
       
   }
}
