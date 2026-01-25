#include <SFML/Graphics.h>
#include <SFML/Window.h>
#include <SFML/audio.h>
#include <iostream>
#include <string>

int gameSize = 6;
using namespace std;

int checkWinner(int** matrix) {
    int winner = 0;
    bool playerOne = true;
    bool playerTwo = true;
   int i = gameSize - 1;
        for (int j = gameSize - 2; j > 0; j--) {
            if (matrix[i][j] == 1) {
                playerOne *= true;
                
            }
            else {
                playerOne *= false;
            }
            
        }
        int j = gameSize - 1;
        for (int i = gameSize - 2; i > 0; i--) {
            if (matrix[i][j] == 2) {
                playerTwo *= true;
            }
            else {
                playerTwo *= false;
            }
           
        }
    
        if (playerOne) {
             winner = 1;
        }
        else if(playerTwo) {
             winner = 2;
        }
        else {
             winner=0;
        }

        return winner;
}
bool checkDraw(int type, int** matrix, int size) {
    bool isDraw = false;
    for (int i = 0; i < size - 1; i++) {
        for (int j = 0; j < size - 1; j++) {
            if (matrix[i][j] == type) {
                if (type == 1) {
                    if (matrix[i + 1][j] > 0 && matrix[i + 2][j] > 0) {
                        isDraw = true;
                    }
                    else {
                        isDraw = false;
                        break;
                    }
                }
                else if (type == 2) {
                    if (matrix[i][j + 1] > 0 && matrix[i][j + 2] > 0) {
                        isDraw = true;
                    }
                    else {
                        isDraw = false;
                        break;
                    }
                }
            }
        }
    }

    return isDraw;
}
int** createMatrix(int** matrix) {
    for (int i = 0; i < gameSize; i++) {
        for (int j = 0; j < gameSize; j++) {
            if ((j == gameSize - 1 && i == 0) || (j == 0 && i == 0) || (j == gameSize - 1 && i == gameSize - 1) || (j == 0 && i == gameSize - 1)) {
                matrix[i][j] = -1;
            }
            else if (i == 0) {
                matrix[i][j] = 1;
            }
            else if (j == 0) {
                matrix[i][j] = 2;
            }
            else {
                matrix[i][j] = 0;
            }

        }
    }
    return matrix;
}
int main()
{
    sfSoundBuffer* moveBuffer = sfSoundBuffer_createFromFile("C:/Users/MoazE/source/repos/AOA_Game/x64/Debug/click-36683.wav");
    if (!moveBuffer) return 1;

    sfSound* moveSound = sfSound_create();
    sfSound_setBuffer(moveSound, moveBuffer);

    sfSoundBuffer* errorBuffer = sfSoundBuffer_createFromFile("C:/Users/MoazE/source/repos/AOA_Game/x64/Debug/asdf.wav");
    if (!errorBuffer) return 1;

    sfSound* errorSound = sfSound_create();
    sfSound_setBuffer(errorSound, errorBuffer);

    sfSoundBuffer* winBuffer = sfSoundBuffer_createFromFile("C:/Users/MoazE/source/repos/AOA_Game/x64/Debug/As.wav");
    if (!winBuffer) return 1;

    sfSound* winSound = sfSound_create();
    sfSound_setBuffer(winSound, winBuffer);

    sfFont* font = sfFont_createFromFile("C:/Windows/Fonts/arial.ttf"); // ? ???? ?? ???? ????
    
    sfText* winText = sfText_create();
    sfText_setFont(winText, font);
    sfText_setCharacterSize(winText, 40);
    sfText_setFillColor(winText, sfColor_fromRGB(255, 255, 0));
   
    sfRenderWindow* window;
    sfVideoMode mode = { gameSize * 100, gameSize * 100, 32 };
    window = sfRenderWindow_create(mode, "Animus_AOA-Game", sfResize | sfClose, NULL);
    if (!window)
        return 1;

    int inMenu = 1; // ? ???? ????????

    // ????? ?? ???????
    sfRectangleShape* startButton = sfRectangleShape_create();
    sfVector2f buttonSize = { 200, 80 };
    sfRectangleShape_setSize(startButton, buttonSize);
    sfVector2f buttonPos = { (gameSize * 100 - 200) / 2, (gameSize * 100 - 80) / 2 };
    sfRectangleShape_setPosition(startButton, buttonPos);
    sfRectangleShape_setFillColor(startButton, sfColor_fromRGB(100, 150, 255));

    // ????? ?? ?????? "?????"

   
    if (!font)
        return 1;

    sfText* startText = sfText_create();
    sfText_setString(startText, "Start");
    sfText_setFont(startText, font);
    sfText_setCharacterSize(startText, 36);
    sfText_setFillColor(startText, sfColor_fromRGB(255, 255, 255));
    sfVector2f textPos = { buttonPos.x + 50, buttonPos.y + 20 };
    sfText_setPosition(startText, textPos);

    // ???? ????? ??????
    sfRectangleShape* cell = sfRectangleShape_create();
    sfVector2f size = { 98, 98 };
    sfRectangleShape_setSize(cell, size);

    sfTexture* greenPieceTexture = sfTexture_createFromFile("C:/Users/MoazE/source/repos/AOA_Game/x64/Debug/GreenRock.png", NULL);
    if (!greenPieceTexture) return 1;
    sfSprite* greenPieceSprite = sfSprite_create();
    sfSprite_setTexture(greenPieceSprite, greenPieceTexture, sfTrue);
    sfVector2f greenPieceSize = { .098, .098 };
    sfSprite_setScale(greenPieceSprite, greenPieceSize);

    sfTexture* redPieceTexture = sfTexture_createFromFile("C:/Users/MoazE/source/repos/AOA_Game/x64/Debug/RedRock.png", NULL);
    if (!redPieceTexture) return 1;
    sfSprite* redPieceSprite = sfSprite_create();
    sfSprite_setTexture(redPieceSprite, redPieceTexture, sfTrue);
    sfVector2f redPieceSize = { .098, .098 };
    sfSprite_setScale(redPieceSprite, redPieceSize);
    sfSprite_setRotation(redPieceSprite, 270);

    int** matrix = new int* [gameSize];
    for (int i = 0; i < gameSize; ++i)
        matrix[i] = new int[gameSize];
    
    matrix = createMatrix(matrix);
    int turn = 1;
    while (sfRenderWindow_isOpen(window))
    {
        sfEvent event;

        while (sfRenderWindow_pollEvent(window, &event))
        {
            if (event.type == sfEvtClosed)
                sfRenderWindow_close(window);

            if (inMenu && event.type == sfEvtMouseButtonPressed && event.mouseButton.button == sfMouseLeft)
            {
                float mouseX = event.mouseButton.x;
                float mouseY = event.mouseButton.y;
                if (mouseX >= buttonPos.x && mouseX <= buttonPos.x + buttonSize.x &&
                    mouseY >= buttonPos.y && mouseY <= buttonPos.y + buttonSize.y)
                {
                    inMenu = 0; // ? ????? ??????
                }
            }
           

            sfRenderWindow_clear(window, sfColor_fromRGB(245, 222, 179));
            
            if (inMenu)
            {
                sfRenderWindow_drawRectangleShape(window, startButton, NULL);
                sfRenderWindow_drawText(window, startText, NULL);
            }
            else
            {
                

                for (int row = 0; row < gameSize; row++)
                {
                    for (int col = 0; col < gameSize; col++)
                    {
                        sfVector2f pos = { col * 100.0f, row * 100.0f };
                        sfRectangleShape_setPosition(cell, pos);

                        if ((row == 0 || row == gameSize - 1) && col != 0 && col < gameSize - 1)
                            sfRectangleShape_setFillColor(cell, sfColor_fromRGB(100, 255, 100));
                        else if ((col == 0 || col == gameSize - 1) && row != 0 && row < gameSize - 1)
                            sfRectangleShape_setFillColor(cell, sfColor_fromRGB(255, 100, 100));
                        else
                            sfRectangleShape_setFillColor(cell, sfColor_fromRGB(200, 200, 200));

                        sfRenderWindow_drawRectangleShape(window, cell, NULL);
                    }
                }
                for (int row = 0; row < gameSize ; row++) {
                    for (int col = 0; col < gameSize; col++) {

                        if (matrix[row][col] == 1) {

                            sfVector2f greenPos = { col * 100.0f + 12.5, row * 100.0f + 12.5 };
                            sfSprite_setPosition(greenPieceSprite, greenPos);
                            sfSprite_setColor(greenPieceSprite, sfColor_fromRGB(0, 255, 0));
                            sfRenderWindow_drawSprite(window, greenPieceSprite, NULL);
                        }
                        if (matrix[row][col] == 2) {
                            sfVector2f redPos = { col * 100.0f + 12.5, row * 100.0f + (100 - 12.5) };
                            sfSprite_setPosition(redPieceSprite, redPos);
                            sfSprite_setColor(redPieceSprite, sfColor_fromRGB(255, 0, 0));
                            sfRenderWindow_drawSprite(window, redPieceSprite, NULL);
                        }
                    }
                }
                if (event.type == sfEvtMouseButtonPressed && checkWinner(matrix)==0) {
                    sfVector2i mousePos = sfMouse_getPositionRenderWindow(window);
                    int col = mousePos.x / 100;
                    int row = mousePos.y / 100;
                    bool Draw=false;
                    if (matrix[row][col] == 1 ) {
                        Draw=checkDraw(1, matrix, gameSize);
                        if (turn == 1) {
                            if (matrix[row + 1][col] == 0) {
                                matrix[row + 1][col] = 1;
                                matrix[row][col] = 0;
                                turn = 2;
                                sfSound_play(moveSound);
                            }
                            else if (matrix[row + 2][col] == 0) {
                                matrix[row + 2][col] = 1;
                                matrix[row][col] = 0;
                                turn = 2;
                                sfSound_play(moveSound);
                            }
                            else {

                                cout << "This rock cannot move\n";
                                
                            }
                            
                            
                        }else{
                            sfSound_play(errorSound);
                        }
                        if (Draw) {
                            turn = 2;
                            cout << "the turn has been changed because of draw" << endl;
                        }
                    }
                    else if (matrix[row][col] == 2) {
                        Draw = checkDraw(2, matrix, gameSize);
                        if (turn == 2) {
                            if (matrix[row][col + 1] == 0) {
                                matrix[row][col + 1] = 2;
                                matrix[row][col] = 0;
                                turn = 1;
                                sfSound_play(moveSound);
                            }
                            else if (matrix[row][col + 2] == 0) {
                                matrix[row][col + 2] = 2;
                                matrix[row][col] = 0;
                                turn = 1;
                                sfSound_play(moveSound);
                            }
                            else {

                                cout << "This rock cannot move\n";
                                
                            }
                            if (Draw) {
                                turn = 1;
                                cout << "the turn has been changed because of draw" << endl;
                            }
                        }
                        else {
                            sfSound_play(errorSound);
                        }
                    }
                    for (int i = 0; i < gameSize; i++) {
                        for (int j = 0; j < gameSize; j++) {
                            cout << matrix[i][j] << "\t";
                        }
                        cout << endl;
                    }
                    cout << "-------------------------" << endl;

                }

                int checker = checkWinner(matrix);
               
                if (checker == 1) {
                    sfText_setString(winText, "Player 1 Wins!");
                    sfVector2f winPos = { 100, (gameSize * 100) / 2.0f };
                    sfText_setPosition(winText, winPos);
                    sfRenderWindow_drawText(window, winText, NULL);
                    sfSound_play(winSound);
                }
                else if (checker == 2) {
                    sfText_setString(winText, "Player 2 Wins!");
                    sfVector2f winPos = { 100, (gameSize * 100) / 2.0f };
                    sfText_setPosition(winText, winPos);
                    sfRenderWindow_drawText(window, winText, NULL);
                    sfSound_play(winSound);
                }
            }



            sfRenderWindow_display(window);
        }
    }
    // ????? ???????
    sfText_destroy(startText);
    sfFont_destroy(font);
    sfRectangleShape_destroy(startButton);
    sfTexture_destroy(greenPieceTexture);
    sfSprite_destroy(greenPieceSprite);
    sfTexture_destroy(redPieceTexture);
    sfSprite_destroy(redPieceSprite);
    sfRectangleShape_destroy(cell);
    sfRenderWindow_destroy(window);
    sfSound_destroy(moveSound);
    sfSoundBuffer_destroy(moveBuffer);
    sfSound_destroy(errorSound);
    sfSoundBuffer_destroy(errorBuffer);
    sfSound_destroy(winSound);
    sfSoundBuffer_destroy(winBuffer);
    
    return 0;
}
