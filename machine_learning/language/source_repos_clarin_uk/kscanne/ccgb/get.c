#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <db.h>

int
main (int argc, char *argv[])
{
  DB *dbp;
  DBT key, data;
  int ret, len, t_ret, showkey_p;
  char token[1024];

  if (argc != 3)
    {
      fprintf (stderr, "Usage: ppfaigh dbfile [y|n]\n");
      exit (1);
    }

  showkey_p = !strcmp(argv[2],"y");

  if ((ret = db_create (&dbp, NULL, 0)) != 0)
    {
      fprintf (stderr, "db_create: %s\n", db_strerror (ret));
      exit (1);
    }
  if ((ret =
       dbp->open (dbp, NULL, argv[1], NULL, DB_HASH, DB_RDONLY, 0)) != 0)
    {
      dbp->err (dbp, ret, "%s", argv[1]);
      goto err;
    }

  while (fgets (token, 1024, stdin) != NULL)
    {
      memset (&key, 0, sizeof (key));
      memset (&data, 0, sizeof (data));
      len = strlen (token);
      token[len - 1] = 0;
      key.size = len;		// includes null
      key.data = token;
      if ((ret = dbp->get (dbp, NULL, &key, &data, 0)) == 0)
	{
	  if (showkey_p) printf ("%s ", (char*) key.data);
	  printf ("%s\n", (char *) data.data);
	}
      else
	{
//       fprintf(stderr, "Could not find key %s\n", key.data);
//       dbp->err (dbp, ret, "DB->get");
//       goto err;
	  ;
	}
    }

err:
  if ((t_ret = dbp->close (dbp, 0)) != 0 && ret == 0)
    ret = t_ret;
  exit (ret);
}
