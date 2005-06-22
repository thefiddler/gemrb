/* GemRB - Infinity Engine Emulator
 * Copyright (C) 2003 The GemRB Project
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 *
 * $Header: /data/gemrb/cvs2svn/gemrb/gemrb/gemrb/plugins/BMPImporter/BMPImp.cpp,v 1.20 2005/06/22 15:55:23 avenger_teambg Exp $
 *
 */

#include "../../includes/win32def.h"
#include "BMPImp.h"
#include "../../includes/RGBAColor.h"
#include "../Core/Interface.h"

BMPImp::BMPImp(void)
{
	str = NULL;
	autoFree = false;
	Palette = NULL;
	pixels = NULL;
}

BMPImp::~BMPImp(void)
{
	if (str && autoFree) {
		delete( str );
	}
	if (Palette) {
		free( Palette );
	}
	if (pixels) {
		free( pixels );
	}
}

bool BMPImp::Open(DataStream* stream, bool autoFree)
{
	if (stream == NULL) {
		return false;
	}
	if (str && this->autoFree) {
		delete( str );
	}
	if (Palette) {
		free( Palette );
	}
	str = stream;
	this->autoFree = autoFree;
	//BITMAPFILEHEADER
	char Signature[2];
	ieDword FileSize, DataOffset;

	str->Read( Signature, 2 );
	if (strncmp( Signature, "BM", 2 ) != 0) {
		printf( "[BMPImporter]: Not a valid BMP File.\n" );
		return false;
	}
	str->ReadDword( &FileSize );
	str->Seek( 4, GEM_CURRENT_POS );
	str->ReadDword( &DataOffset );

	//BITMAPINFOHEADER

	str->ReadDword( &Size );
	str->ReadDword( &Width );
	str->ReadDword( &Height );
	str->ReadWord( &Planes );
	str->ReadWord( &BitCount );
	str->ReadDword( &Compression );
	str->ReadDword( &ImageSize );
	str->Seek( 16, GEM_CURRENT_POS );
	//str->Read(&Hres, 4);
	//str->Read(&Vres, 4);
	//str->Read(&ColorsUsed, 4);
	//str->Read(&ColorsImportant, 4);
	if (Compression != 0) {
		printf( "[BMPImporter]: Compressed %d-bits Image, Not Supported.",
			BitCount );
		return false;
	}
	//COLORTABLE
	Palette = NULL;
	if (BitCount <= 8) {
		if (BitCount == 8)
			NumColors = 256;
		else
			NumColors = 16;
		Palette = ( Color * ) malloc( 4 * NumColors );
		//no idea if we have to swap this or not
		for (unsigned int i = 0; i < NumColors; i++) {
			str->Read( &Palette[i].b, 1 );
			str->Read( &Palette[i].g, 1 );
			str->Read( &Palette[i].r, 1 );
			str->Read( &Palette[i].a, 1 );
		}
	}
	str->Seek( DataOffset, GEM_STREAM_START );
	//no idea if we have to swap this or not
	//RASTERDATA
	switch (BitCount) {
		case 24:
			PaddedRowLength = Width * 3;
			break;

		case 16:
			PaddedRowLength = Width * 2;
			break;

		case 8:
			PaddedRowLength = Width;
			break;

		case 4:
			PaddedRowLength = ( Width >> 1 );
			break;
		default:
			printf( "[BMPImporter]: BitCount not supported.\n" );
			return false;
	}
	//if(BitCount!=4)
	//{
	if (PaddedRowLength & 3) {
		PaddedRowLength += 4 - ( PaddedRowLength & 3 );
	}
	//}
	void* rpixels = malloc( PaddedRowLength* Height );
	str->Read( rpixels, PaddedRowLength * Height );
	if (BitCount == 24) {
		int size = Width * Height * 3;
		pixels = malloc( size );
		unsigned char * dest = ( unsigned char * ) pixels;
		dest += size;
		unsigned char * src = ( unsigned char * ) rpixels;
		for (int i = Height; i; i--) {
			dest -= ( Width * 3 );
			memcpy( dest, src, Width * 3 );
			src += PaddedRowLength;
		}
	} else if (BitCount == 8) {
		pixels = malloc( Width * Height );
		unsigned char * dest = ( unsigned char * ) pixels;
		dest += Height * Width;
		unsigned char * src = ( unsigned char * ) rpixels;
		for (int i = Height; i; i--) {
			dest -= Width;
			memcpy( dest, src, Width );
			src += PaddedRowLength;
		}
	} else if (BitCount == 4) {
		int size = PaddedRowLength * Height;
		pixels = malloc( size );
		unsigned char * dest = ( unsigned char * ) pixels;
		dest += size;
		unsigned char * src = ( unsigned char * ) rpixels;
		for (int i = Height; i; i--) {
			dest -= PaddedRowLength;
			memcpy( dest, src, PaddedRowLength );
			src += PaddedRowLength;
		}
	}
	free( rpixels );
	return true;
}

Sprite2D* BMPImp::GetImage()
{
	Sprite2D* spr = NULL;
	if (BitCount == 24) {
		void* p = malloc( Width * Height * 3 );
		memcpy( p, pixels, Width * Height * 3 );
		spr = core->GetVideoDriver()->CreateSprite( Width, Height, 24,
			0x00ff0000, 0x0000ff00, 0x000000ff, 0x00000000, p,
			true, 0x0000ff00 );
	} else if (BitCount == 8) {
		void* p = malloc( Width* Height );
		memcpy( p, pixels, Width * Height );
		spr = core->GetVideoDriver()->CreateSprite8( Width, Height, 8,
			p, Palette, true, 0 );
	} else if (BitCount == 4) {
		void* p = malloc( Width* Height );
		unsigned char * dst = ( unsigned char * ) p;
		for (unsigned int y = 0; y < Height; y++) {
			unsigned char * src = ( unsigned char * ) pixels +
				( PaddedRowLength * y );
			for (unsigned int x = 0; x < Width; x++) {
				*dst = ( *src >> 4 );
				dst++;
				if (x == ( Width - 1 ))
					if (!( Width & 1 ))
						continue;
				*dst = ( *src & 0x0f );
				dst++;
				src++;
				x++;
			}
		}
		spr = core->GetVideoDriver()->CreateSprite8( Width, Height, 4,
			p, Palette, false );
	}
	return spr;
}
/** No descriptions */
void BMPImp::GetPalette(int index, int colors, Color* pal)
{
	if (BitCount == 24) {
		unsigned char * p = ( unsigned char * ) pixels;
		p += PaddedRowLength * index;
		for (int i = 0; i < colors; i++) {
			pal[i].b = *p++;
			pal[i].g = *p++;
			pal[i].r = *p++;
		}
	} else if (BitCount == 8) {
		int p = index;
		for (int i = 0; i < colors; i++) {
			pal[i].r = Palette[p].r;
			pal[i].g = Palette[p].g;
			pal[i].b = Palette[p++].b;
		}
	}
}
