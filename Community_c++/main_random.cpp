#include<iostream>

using namespace std;

char *outfile  = NULL;

int
main(int argc, char **argv) {    //argcΪ����argv�ĳ��ȣ�argv[0]Ϊ��ǰ�ļ�·�� 
  srand(time(NULL));

  int n = atoi(argv[1]);
  int degree = atoi(argv[2]);

  for (unsigned int i=0 ; i<n ; i++) {
    for (unsigned int j=0 ; j<n ; j++) {
      int r  = rand()%n;
      if (r<degree)
        cout << i << " " << j << endl;
    }
  }
  system("pause");
  return 0;
}
