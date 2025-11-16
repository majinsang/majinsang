#include <windows.h>
#include <iostream>

void SendKeyInput(WORD vKey, bool isKeyDown)
{
    INPUT input = { 0 }; 
    input.type = INPUT_KEYBOARD;

    input.ki.wVk = vKey;

    if (!isKeyDown)
    {
        input.ki.dwFlags = KEYEVENTF_KEYUP;
    }

    SendInput(1, &input, sizeof(INPUT));
}

int main()
{
    std::cout << "after 3 second, test start."<< std::endl;

    Sleep(3000); 

    SendKeyInput('W', true);

    Sleep(1000); 

    SendKeyInput('W', false);
    
    SendKeyInput('A', true);

    Sleep(1000); 

    SendKeyInput('A', false);

    SendKeyInput('S', true);

    Sleep(1000);

    SendKeyInput('S', false);

    SendKeyInput('D', true);

    Sleep(1000);

    SendKeyInput('D', false);

    SendKeyInput(VK_SPACE, true);

    Sleep(100);

    SendKeyInput(VK_SPACE, false);

    std::cout << "good" << std::endl;
    

    return 0;
}