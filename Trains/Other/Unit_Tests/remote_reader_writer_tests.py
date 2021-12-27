import asyncio
import unittest
import sys
sys.path.append('../../../')
from Trains.Remote.server_proxy import ServerProxy


class RemoteReaderWriterTest(unittest.TestCase):
    async def test_server_proxy_sign_up_with_server(self):
        reader, writer = await asyncio.open_connection(
            '127.0.0.1', 8888)
        server_proxy = ServerProxy("name", 8000, "playername", "Buy-Now",reader, writer)
        server_proxy.sign_up_with_server()
        self.assertEqual(server_proxy.server_reader.read(), "playernamebobaosfdasfldsflasd")


if __name__ == '__main__':
    unittest.main()
