import logging


def init_logger():
	logging.basicConfig(
		filename='status.log',
		filemode='w',
		format='{asctime} {name} - [{levelname}] {message}',
		datefmt='%d/%m/%Y %I:%M:%S %p',
		style='{',
		level=logging.DEBUG,
		encoding='utf-8'
	)


	logger = logging.getLogger('BURG.L Operations Log')
	logger.info('BURG.L Operations Log initialised.')
