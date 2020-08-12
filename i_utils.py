"""
 my ulitites
 Author: Ilnur Sayfutdinov
 E-mail: ilnursoft@gmail.com
"""

import requests
import asyncio


# преобразование строки вида "SAMSUNG a50 64\\xd0\\xb3\\xd0\\xb1" в строку c кодировкой encoding
def string_escape(s, encoding="utf-8"):
    import codecs
    byte_s = bytes(s, encoding)
    res = codecs.escape_decode(byte_s)[0]
    res = res.decode(encoding)
    return res


# сохранить в файл html из urls
# True - если смогли получить данные с запроса и сохранить в файл
def savefile_from_url(urls=None, filename="test.html"):
    if urls is None:
        return False
    session = requests.Session()
    r = session.get(urls)
    print(r.status_code)

    if (r.status_code == 200):
        # print(r.headers)
        # print(r.content)
        html = str(r.content)
        with open(filename, "w") as f:
            f.write(html)
        return True

    return False


# запуск команды cmd asyncio
async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    
    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')    
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')          
    # if stderr:
    #     print(f'[stderr]\n{stderr.decode()}')

    return stdout, stderr, proc.returncode

    