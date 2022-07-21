from logging import basicConfig, DEBUG


def init_logger(filepath):
	basicConfig(
		filename=f'{filepath}/status.log',
		filemode='w',
		format='{asctime} {name} - [{levelname}] {message}',
		datefmt='%d/%m/%Y %I:%M:%S %p',
		style='{',
		level=DEBUG,
		encoding='utf-8'
	)
