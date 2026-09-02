import sys
from typing import List

from src.shared.models import MatchEvent

class MatchEventOutputStream:
    def __init__(self, destination_stream, event_array: List[MatchEvent], count: int):
        """
        Construtor da subclasse/wrapper de fluxo de saída (Questão 1-a).
        
        :param destination_stream: O objeto de destino para onde os dados serão enviados.
                                   Pode ser: sys.stdout, um arquivo aberto para escrita ('w' ou 'wb'),
                                   ou um objeto de socket TCP conectado.
        :param event_array: Lista (array) contendo instâncias de objetos MatchEvent.
        :param count: O número exato de objetos do array que deverão ser enviados pelo stream.
        """
        self.destination = destination_stream
        self.events = event_array
        self.count = min(int(count), len(event_array))

    def write_all(self) -> None:
        """
        Percorre a quantidade 'count' de objetos do array, serializa cada um deles
        para texto delimitado por formato CSV e despacha os bytes para o destino configurado.
        """
        for i in range(self.count):
            event = self.events[i]
            csv_line = event.to_csv_line()
            
            if self.destination == sys.stdout:
                sys.stdout.write(csv_line)
                sys.stdout.flush()
                
            elif hasattr(self.destination, "sendall"):
                data_bytes = csv_line.encode("utf-8")
                self.destination.sendall(data_bytes)
                
            else:
                if hasattr(self.destination, "write"):
                    if "b" in getattr(self.destination, "mode", ""):
                        self.destination.write(csv_line.encode("utf-8"))
                    else:
                        self.destination.write(csv_line)
