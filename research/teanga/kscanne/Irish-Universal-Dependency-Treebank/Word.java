/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


/**
 *
 * @author fosterjen
 */
public class Word 
{
    String token;
    String lemma;
    String posFine;
    String posCoarse;
    String relation;
    int head;
    int id;
    String wordConll;
    
    public Word(String line)
    {
        wordConll = line;
        String [] tokens = line.split("\t");
        id = Integer.parseInt(tokens[0]);
        token = tokens[1];
        lemma = tokens[2];
        posFine = tokens[3];
        posCoarse = tokens[4];
        head = Integer.parseInt(tokens[6]);
        relation = tokens[7];
    }
    
    public String getToken()
    {
        return token;
    }
    
    public void setToken(String s)
    {
        token = s;
    }
    
    public int getId()
    {
        return id;
    }
    
    public String getLemma()
    {
        return lemma;
    }
    
    public int getHead()
    {
        return head;
    }
    
    public void setHead(int h)
    {
        head = h;
    }
    
    public String getRelation()
    {
        return relation;
    }
    
    public void setRelation(String r)
    {
        relation = r;
    }

    public String getPosCoarse()
    {
	return posCoarse;
    }
    
    public String toString()
    {
        return id + "\t" + token + "\t" + lemma + "\t" + posFine + "\t" + posCoarse + "\t_\t" + head + "\t" + relation + "\t_\t_";
    }
}
