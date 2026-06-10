#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <db.h>

#define MAXDATASZ 2097152

int
main (int argc, char *argv[])
{
  DB *dbp;
  DBT key, data;
  int ret, len, t_ret;
  char token[MAXDATASZ];
  char *split;

  if (argc != 2)
    {
      fprintf (stderr, "Usage: pptog dbfile\n");
      exit (1);
    }

  if ((ret = db_create (&dbp, NULL, 0)) != 0)
    {
      fprintf (stderr, "db_create: %s\n", db_strerror (ret));
      exit (1);
    }
  if ((ret =
       dbp->open (dbp, NULL, argv[1], NULL, DB_HASH, DB_CREATE, 0664)) != 0)
    {
      dbp->err (dbp, ret, "%s", argv[1]);
      goto err;
    }

  while (fgets (token, MAXDATASZ, stdin) != NULL)
    {
      memset (&key, 0, sizeof (key));
      memset (&data, 0, sizeof (data));
      split = strchr (token, ' ');
      if (split == NULL)
	{
	  split = strchr (token, '\n');
	  if (split == NULL)
	    {
	      fprintf (stderr, "Neither a space nor a newline.\n");
	      continue;
	    }
	}
      // keep null characters at end of all keys/data in db 
      key.size = split - token + 1;
      *split = 0;
      key.data = token;
      len = strlen (split + 1);
      if (len == 0)
	len = 1;
      *(split + len) = 0;	/* was newline */
      data.size = len;
      data.data = split + 1;
      if ((ret = dbp->put (dbp, NULL, &key, &data, 0)) == 0)
	{
	  printf ("db: %s: key stored.\n", (char *) key.data);
	  ;
	}
      else
	{
	  dbp->err (dbp, ret, "DB->put");
	  goto err;
	}
    }

err:if ((t_ret = dbp->close (dbp, 0)) != 0 && ret == 0)
    ret = t_ret;
  exit (ret);
}
